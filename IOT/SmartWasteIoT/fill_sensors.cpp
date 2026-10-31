#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>
#include "fill_sensors.h"
#include "actuator_control.h"
#include "iot_logic.h"

namespace {
QueueHandle_t reportQueue = nullptr;
constexpr unsigned long ECHO_TIMEOUT_US = 25000;
static_assert(FILL_SAMPLES_PER_BIN > 0, "Sample count must be positive");
static_assert(FILL_TRIM_LOW < FILL_SAMPLES_PER_BIN &&
                  FILL_TRIM_HIGH < FILL_SAMPLES_PER_BIN - FILL_TRIM_LOW,
              "Trimming must leave at least one sample");
static_assert(FILL_SAMPLE_INTERVAL_MS >= 60, "HC-SR04 needs a gap between ultrasonic bursts");
static_assert(FILL_INTERVAL_MS >= 3UL * FILL_SAMPLES_PER_BIN * FILL_SAMPLE_INTERVAL_MS,
              "Fill cycle must allow enough time to sample all three bins");

float measureDistance(int index) {
  digitalWrite(SENSOR_TRIG_PINS[index], LOW);
  delayMicroseconds(2);
  digitalWrite(SENSOR_TRIG_PINS[index], HIGH);
  delayMicroseconds(10);
  digitalWrite(SENSOR_TRIG_PINS[index], LOW);
  const unsigned long duration = pulseIn(SENSOR_ECHO_PINS[index], HIGH, ECHO_TIMEOUT_US);
  if (duration == 0) return -1.0f;
  const float cm = duration / 58.0f;
  return cm >= 2.0f && cm <= 400.0f ? cm : -1.0f;
}

void sensorTask(void *) {
  for (;;) {
    // Neo vao chu ky thuc te; khong chay don nhieu chu ky khi bi tre.
    TickType_t cycleStart = xTaskGetTickCount();
    FillReport report = {};
    for (int i = 0; i < 3; ++i) {
      iot::DistanceSamples<FILL_SAMPLES_PER_BIN> samples;
      uint32_t initialVersion = 0;
      FillReading &reading = report.bins[i];
      reading.lidUnstable = !getClosedLidVersion(i, &initialVersion);
      reading.lidVersion = initialVersion;
      if (!reading.lidUnstable) {
        for (unsigned int sample = 0; sample < FILL_SAMPLES_PER_BIN; ++sample) {
          uint32_t version = 0;
          if (!getClosedLidVersion(i, &version) || version != initialVersion) {
            reading.lidUnstable = true;
            break;
          }
          TickType_t sampleStart = xTaskGetTickCount();
          samples.add(measureDistance(i));
          reading.measuredAtMs = millis();
          reading.measuredAtUtc = time(nullptr);
          // Tat ca cam bien dung chung task, khong phat sieu am dong thoi.
          // Bat dau moi lan do cach nhau khoang 70ms, khong cong don timeout.
          // Lan cuoi van nghi de tranh nhieu khi chuyen sang cam bien khac.
          vTaskDelayUntil(&sampleStart, pdMS_TO_TICKS(FILL_SAMPLE_INTERVAL_MS));
        }
        uint32_t finalVersion = 0;
        if (!getClosedLidVersion(i, &finalVersion) || finalVersion != initialVersion) {
          reading.lidUnstable = true;
        }
      }
      // Du 10 mau: bo 3 nho nhat, 1 lon nhat, lay trung binh 6 mau con lai.
      reading.validSamples = samples.count;
      reading.distanceCm = samples.trimmedMean(FILL_TRIM_LOW, FILL_TRIM_HIGH);
      reading.minCm = samples.count > 0 ? samples.minCm : -1.0f;
      reading.maxCm = samples.count > 0 ? samples.maxCm : -1.0f;
    }
    // Chi giu chu ky moi nhat: mat mang khong tich luu hang doi so do cu.
    xQueueOverwrite(reportQueue, &report);
    vTaskDelayUntil(&cycleStart, pdMS_TO_TICKS(FILL_INTERVAL_MS));
  }
}
}  // namespace

bool setupFillSensors() {
  for (int i = 0; i < 3; ++i) {
    pinMode(SENSOR_TRIG_PINS[i], OUTPUT);
    digitalWrite(SENSOR_TRIG_PINS[i], LOW);
    pinMode(SENSOR_ECHO_PINS[i], INPUT);
  }
  reportQueue = xQueueCreate(1, sizeof(FillReport));
  if (reportQueue == nullptr) return false;
  if (xTaskCreate(sensorTask, "iot-fill", 4096, nullptr, 1, nullptr) != pdPASS) {
    vQueueDelete(reportQueue);
    reportQueue = nullptr;
    return false;
  }
  Serial.printf("[Sensor] San sang: 3 HC-SR04, %u mau/thung, cach nhau %lu ms, chu ky %lu ms\n",
                FILL_SAMPLES_PER_BIN, FILL_SAMPLE_INTERVAL_MS, FILL_INTERVAL_MS);
  Serial.printf("[Sensor] Bo %u mau nho nhat va %u mau lon nhat, lay trung binh %u mau con lai\n",
                FILL_TRIM_LOW, FILL_TRIM_HIGH, FILL_SAMPLES_PER_BIN - FILL_TRIM_LOW - FILL_TRIM_HIGH);
  return true;
}

bool takeFillReport(FillReport *report) {
  return reportQueue != nullptr && report != nullptr && xQueueReceive(reportQueue, report, 0) == pdTRUE;
}
