#include <Arduino.h>
#include <ESP32Servo.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>
#include "actuator_control.h"
#include "iot_logic.h"

namespace {
Servo lidServos[3];
QueueHandle_t commandQueue = nullptr;
struct ActuatorCommand {
  int binIndex;
  uint32_t enqueuedAtMs;
};
const char *const binNames[3] = {"recyclable", "organic", "inorganic"};
portMUX_TYPE lidStateMux = portMUX_INITIALIZER_UNLOCKED;
bool closedState[3] = {};
unsigned long closedAt[3] = {};
uint32_t lidVersions[3] = {};

void markLidState(int index, bool closed) {
  const unsigned long now = millis();
  portENTER_CRITICAL(&lidStateMux);
  closedState[index] = closed;
  closedAt[index] = now;
  ++lidVersions[index];
  portEXIT_CRITICAL(&lidStateMux);
}

void releaseActuators() {
  for (int i = 0; i < 3; ++i) {
    lidServos[i].detach();
    markLidState(i, false);
  }
  if (commandQueue != nullptr) {
    vQueueDelete(commandQueue);
    commandQueue = nullptr;
  }
}

void actuatorTask(void *) {
  bool lidOpen[3] = {};
  unsigned long openedAt[3] = {};
  bool greenOn = false;
  bool redOn = false;
  unsigned long greenAt = 0;
  unsigned long redAt = 0;

  for (;;) {
    const unsigned long now = millis();
    // Xu ly timer truoc, ke ca khi hang doi dang co nhieu lenh.
    for (int i = 0; i < 3; ++i) {
      if (lidOpen[i] && now - openedAt[i] >= LID_OPEN_MS) {
        markLidState(i, true);
        lidServos[i].write(SERVO_CLOSED_ANGLES[i]);
        lidOpen[i] = false;
        Serial.printf("[Servo] Dong %s: %d do\n", binNames[i], SERVO_CLOSED_ANGLES[i]);
      }
    }
    if (greenOn && now - greenAt >= LED_ON_MS) {
      digitalWrite(LED_GREEN_PIN, LOW);
      greenOn = false;
      Serial.println("[LED] Tat xanh");
    }
    if (redOn && now - redAt >= LED_ON_MS) {
      digitalWrite(LED_RED_PIN, LOW);
      redOn = false;
      Serial.println("[LED] Tat do");
    }

    ActuatorCommand command;
    if (xQueueReceive(commandQueue, &command, 0) == pdTRUE) {
      if (iot::elapsed(millis(), command.enqueuedAtMs, ACTUATOR_QUEUE_MAX_AGE_MS)) {
        Serial.println("[Servo] Bo lenh doi qua 2 giay trong hang doi");
        vTaskDelay(pdMS_TO_TICKS(10));
        continue;
      }
      const int binIndex = command.binIndex;
      if (binIndex == -1) {
        digitalWrite(LED_RED_PIN, HIGH);
        redOn = true;
        redAt = millis();
        Serial.println("[LED] Bat do: AI khong tu tin, khong mo them nap");
      } else if (binIndex >= 0 && binIndex < 3) {
        markLidState(binIndex, false);
        lidServos[binIndex].write(SERVO_OPEN_ANGLES[binIndex]);
        lidOpen[binIndex] = true;
        openedAt[binIndex] = millis();
        digitalWrite(LED_GREEN_PIN, HIGH);
        greenOn = true;
        greenAt = openedAt[binIndex];
        Serial.printf("[Servo] Mo %s: %d do, tu dong sau %lu ms\n",
                      binNames[binIndex], SERVO_OPEN_ANGLES[binIndex], LID_OPEN_MS);
        Serial.println("[LED] Bat xanh");
      }
    }
    // Nhuong CPU cua task nay; khong chan vong lap Wi-Fi/MQTT.
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}
}  // namespace

bool setupActuators() {
  if (commandQueue != nullptr) return true;
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_GREEN_PIN, LOW);
  bool attachedAll = true;
  for (int i = 0; i < 3; ++i) {
    lidServos[i].setPeriodHertz(50);
    lidServos[i].attach(SERVO_PINS[i]);
    if (!lidServos[i].attached()) {
      attachedAll = false;
      Serial.printf("[Servo] Loi attach GPIO %d\n", SERVO_PINS[i]);
    } else {
      markLidState(i, true);
      lidServos[i].write(SERVO_CLOSED_ANGLES[i]);
    }
  }
  if (!attachedAll) {
    releaseActuators();
    return false;
  }

  commandQueue = xQueueCreate(8, sizeof(ActuatorCommand));
  if (commandQueue == nullptr) {
    releaseActuators();
    return false;
  }
  if (xTaskCreate(actuatorTask, "iot-actuators", 4096, nullptr, 1, nullptr) != pdPASS) {
    releaseActuators();
    return false;
  }
  Serial.println("[Servo] San sang: dong 180 do, mo 100 do, giu 5 giay");
  return true;
}

bool queueActuatorCommand(int binIndex) {
  if (commandQueue == nullptr || binIndex < -1 || binIndex > 2) return false;
  ActuatorCommand command = {binIndex, static_cast<uint32_t>(millis())};
  return xQueueSend(commandQueue, &command, 0) == pdTRUE;
}

bool getClosedLidVersion(int binIndex, uint32_t *version) {
  if (binIndex < 0 || binIndex > 2 || version == nullptr) return false;
  portENTER_CRITICAL(&lidStateMux);
  const bool closed = closedState[binIndex];
  const unsigned long settledFrom = closedAt[binIndex];
  *version = lidVersions[binIndex];
  portEXIT_CRITICAL(&lidStateMux);
  return closed && millis() - settledFrom >= LID_SETTLE_MS;
}
