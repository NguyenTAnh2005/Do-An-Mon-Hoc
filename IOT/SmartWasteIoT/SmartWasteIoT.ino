// Servo/LED va 3 HC-SR04, gui khoang cach da loc qua MQTT khoang moi 7 giay.

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <MQTT.h>  // MQTT cua Joel Gaehwiler (256dpi), cai bang Library Manager.
#include <ArduinoJson.h>  // ArduinoJson 7 cua Benoit Blanchon.
#include <cmath>
#include <cstring>
#include <time.h>
#include "secrets.h"
#include "mqtt_ca.h"
#include "actuator_control.h"
#include "fill_sensors.h"
#include "iot_logic.h"

static_assert(AREA_NUMBER == 1 || AREA_NUMBER == 2, "AREA_NUMBER must be 1 or 2");

constexpr unsigned long SERIAL_BAUD = 115200;
constexpr unsigned long REPORT_INTERVAL_MS = 10000;
constexpr unsigned long WIFI_RETRY_INTERVAL_MS = 15000;
constexpr unsigned long TIME_CHECK_INTERVAL_MS = 1000;
constexpr unsigned long NTP_WAIT_REPORT_MS = 30000;
constexpr time_t MIN_VALID_TIME = 1704067200;  // 2024-01-01 UTC, loai gio mac dinh.
unsigned long lastReportMs = 0;
unsigned long lastWiFiAttemptMs = 0;
unsigned long lastTimeCheckMs = 0;
unsigned long lastNtpWaitReportMs = 0;
bool wifiConfigured = false;
bool wifiWasConnected = false;
bool ntpStarted = false;
bool timeReady = false;
bool configurationReady = false;
bool actuatorsReady = false;
bool sensorsReady = false;

WiFiClientSecure mqttPublishNet;
WiFiClientSecure mqttSubscribeNet;
MQTTClient mqttPublisher(1024);
MQTTClient mqttSubscriber(1024);
constexpr unsigned long MQTT_RETRY_INTERVAL_MS = 15000;
unsigned long lastMqttPublishAttemptMs = 0;
unsigned long lastMqttSubscribeAttemptMs = 0;
bool mqttPublishAttempted = false;
bool mqttSubscribeAttempted = false;
String mqttPublishId;
String mqttSubscribeId;
String mqttStatusTopic;
String mqttClassificationTopic;
String mqttUncertainTopic;
String mqttFillTopics[3];
constexpr size_t LOG_ID_CACHE_SIZE = 32;
iot::RecentLogIds<LOG_ID_CACHE_SIZE> processedLogIds;
bool mqttSubscriptionsReady = false;
bool mqttNetworkAvailable = false;
bool publishedStatusKnown = false;
bool publishedOnline = false;
bool serialTestPending = false;
unsigned long serialTestStartedAt = 0;
unsigned long serialTestSequence = 0;
String serialTestPayload;

void onMqttMessage(String &topic, String &payload) {
  Serial.print("[MQTT RX] ");
  Serial.println(topic);
  Serial.println(payload);
  if (topic != mqttClassificationTopic && topic != mqttUncertainTopic) return;

  JsonDocument message;
  DeserializationError error = deserializeJson(message, payload, DeserializationOption::NestingLimit(4));
  if (error || !message.is<JsonObject>()) {
    Serial.println("[MQTT] Bo qua: JSON khong hop le");
    return;
  }
  const char *timestamp = message["timestamp"] | "";
  if (!timeReady || !iot::isFreshTimestamp(timestamp, static_cast<int64_t>(time(nullptr)))) {
    Serial.println("[MQTT] Bo qua: timestamp sai UTC, cu qua 30 giay hoac som qua 5 giay");
    return;
  }
  if (topic == mqttUncertainTopic) {
    if (!queueActuatorCommand(-1)) Serial.println("[Servo] Chua san sang hoac hang doi day");
    return;
  }

  const char *logId = message["log_id"] | "";
  const char *wasteType = message["waste_type"] | "";
  if (!iot::isUuid(logId) || message["confidence"].is<bool>() || !message["confidence"].is<double>()) {
    Serial.println("[MQTT] Bo qua: log_id hoac confidence khong hop le");
    return;
  }
  const double confidence = message["confidence"].as<double>();
  if (!std::isfinite(confidence) || confidence < 0 || confidence > 1) {
    Serial.println("[MQTT] Bo qua: confidence ngoai khoang 0..1");
    return;
  }
  int binIndex = -1;
  if (strcmp(wasteType, "recyclable") == 0) binIndex = 0;
  else if (strcmp(wasteType, "organic") == 0) binIndex = 1;
  else if (strcmp(wasteType, "inorganic") == 0) binIndex = 2;
  if (binIndex < 0) {
    Serial.println("[MQTT] Bo qua: waste_type khong hop le");
    return;
  }

  // Cache tu chuan hoa UUID; chi nho khi lenh da vao hang doi.
  if (processedLogIds.contains(logId)) {
    Serial.println("[MQTT] Bo qua log_id trung, khong mo lai nap");
    return;
  }
  if (queueActuatorCommand(binIndex)) {
    processedLogIds.remember(logId);
  } else {
    Serial.println("[Servo] Chua san sang hoac hang doi day; lenh chua duoc xu ly");
  }
}

void updateSerialTest() {
  if (serialTestPending && millis() - serialTestStartedAt >= 6500) {
    serialTestPending = false;
    Serial.println("[TEST] Lan 2: xu ly lai cung log_id. Nap KHONG duoc mo lai.");
    onMqttMessage(mqttClassificationTopic, serialTestPayload);
    serialTestPayload = "";
    Serial.println("[TEST] Xong. Kiem tra dong 'Bo qua log_id trung' va nap chi mo mot lan.");
  }

  while (Serial.available() > 0) {
    const char command = static_cast<char>(Serial.read());
    if (command != 't' && command != 'T') continue;
    if (serialTestPending) {
      Serial.println("[TEST] Dang test, cho khoang 7 giay roi thu lai.");
      continue;
    }
    char timestamp[21];
    if (!getUtcTimestamp(timestamp, sizeof(timestamp))) {
      Serial.println("[TEST] Cho NTP dong bo thanh cong roi gui lai chu t.");
      continue;
    }
    char testId[37];
    snprintf(testId, sizeof(testId), "%08lx-0000-4000-8000-%012llx",
             ++serialTestSequence, static_cast<unsigned long long>(ESP.getEfuseMac() & 0xFFFFFFFFFFFFULL));
    JsonDocument message;
    message["log_id"] = testId;
    message["waste_type"] = "organic";
    message["confidence"] = 0.9;
    message["timestamp"] = timestamp;
    serialTestPayload = "";
    serializeJson(message, serialTestPayload);
    Serial.println("[TEST] Test noi bo, khong publish len broker. Tam dung AI de de quan sat.");
    Serial.println("[TEST] Lan 1: mo nap huu co 5 giay; sau do tu thu lenh trung.");
    onMqttMessage(mqttClassificationTopic, serialTestPayload);
    if (!processedLogIds.contains(testId)) {
      serialTestPayload = "";
      Serial.println("[TEST] Chua dua duoc lenh vao hang doi. Xem log loi phia tren roi thu lai.");
      continue;
    }
    serialTestStartedAt = millis();
    serialTestPending = true;
  }
}

void setupMqtt() {
  String deviceId = String(static_cast<unsigned long long>(ESP.getEfuseMac()), HEX);
  String prefix = "school/area" + String(AREA_NUMBER);
  mqttPublishId = "iot-area" + String(AREA_NUMBER) + "-" + deviceId + "-pub";
  mqttSubscribeId = "iot-area" + String(AREA_NUMBER) + "-" + deviceId + "-sub";
  mqttStatusTopic = prefix + "/status/iot";
  mqttClassificationTopic = prefix + "/classification";
  mqttUncertainTopic = prefix + "/uncertain";
  const char *const wasteTypes[3] = {"recyclable", "organic", "inorganic"};
  for (int i = 0; i < 3; ++i) mqttFillTopics[i] = prefix + "/fill_level/" + wasteTypes[i];

  mqttPublishNet.setCACert(MQTT_ROOT_CA);
  mqttSubscribeNet.setCACert(MQTT_ROOT_CA);
  mqttPublishNet.setHandshakeTimeout(5);  // Giay, gioi han moi lan bat tay TLS.
  mqttSubscribeNet.setHandshakeTimeout(5);
  mqttPublisher.begin(MQTT_HOST, MQTT_PORT, mqttPublishNet);
  mqttSubscriber.begin(MQTT_HOST, MQTT_PORT, mqttSubscribeNet);
  mqttPublisher.setOptions(30, true, 2000);
  mqttSubscriber.setOptions(30, true, 2000);
  mqttPublisher.setWill(mqttStatusTopic.c_str(), "{\"status\":\"offline\"}", true, 1);
  mqttSubscriber.onMessage(onMqttMessage);
  Serial.printf("[IoT] Khu vuc %u, MQTT PUB ID: %s\n", AREA_NUMBER, mqttPublishId.c_str());
  Serial.print("[IoT] MQTT SUB ID: ");
  Serial.println(mqttSubscribeId);
}

void printMqttError(const char *label, MQTTClient &client, WiFiClientSecure &net) {
  Serial.printf("[MQTT %s] Loi: lastError=%d, returnCode=%d\n",
                label, static_cast<int>(client.lastError()), static_cast<int>(client.returnCode()));
  char tlsError[160] = {};
  int tlsCode = net.lastError(tlsError, sizeof(tlsError));
  if (tlsCode != 0) {
    Serial.printf("[TLS] %d: %s\n", tlsCode, tlsError);
  }
}

void updateMqtt() {
  if (WiFi.status() != WL_CONNECTED) {
    // Dong TCP khi mat Wi-Fi. Broker xu ly LWT; khong gui DISCONNECT sach.
    if (mqttNetworkAvailable) {
      mqttPublishNet.stop();
      mqttSubscribeNet.stop();
      mqttPublishAttempted = false;
      mqttSubscribeAttempted = false;
    }
    mqttNetworkAvailable = false;
    mqttSubscriptionsReady = false;
    publishedStatusKnown = false;
    return;
  }
  mqttNetworkAvailable = true;
  if (!timeReady) {
    return;  // Cho NTP de kiem tra thoi han chung chi TLS.
  }

  if (mqttPublisher.connected()) mqttPublisher.loop();
  if (mqttSubscriber.connected()) mqttSubscriber.loop();
  if (!mqttSubscriber.connected()) mqttSubscriptionsReady = false;

  unsigned long now = millis();
  if (!mqttPublisher.connected() &&
      (!mqttPublishAttempted || now - lastMqttPublishAttemptMs >= MQTT_RETRY_INTERVAL_MS)) {
    mqttPublishAttempted = true;
    Serial.println("[MQTT PUB] Dang ket noi TLS...");
    if (mqttPublisher.connect(mqttPublishId.c_str(), MQTT_PUBLISH_USER, MQTT_PUBLISH_PASSWORD)) {
      Serial.println("[MQTT PUB] Ket noi thanh cong!");
      publishedStatusKnown = false;  // Se gui trang thai theo ca PUB, SUB va phan cung.
    } else {
      printMqttError("PUB", mqttPublisher, mqttPublishNet);
    }
    lastMqttPublishAttemptMs = millis();
    return;  // Moi vong loop chi thu ket noi mot client.
  }

  now = millis();
  if (!mqttSubscriber.connected() &&
      (!mqttSubscribeAttempted || now - lastMqttSubscribeAttemptMs >= MQTT_RETRY_INTERVAL_MS)) {
    mqttSubscribeAttempted = true;
    Serial.println("[MQTT SUB] Dang ket noi TLS...");
    if (mqttSubscriber.connect(mqttSubscribeId.c_str(), MQTT_SUBSCRIBE_USER, MQTT_SUBSCRIBE_PASSWORD)) {
      Serial.println("[MQTT SUB] Ket noi thanh cong!");
      bool classificationOk = mqttSubscriber.subscribe(mqttClassificationTopic, 1);
      bool uncertainOk = mqttSubscriber.subscribe(mqttUncertainTopic, 1);
      if (classificationOk && uncertainOk) {
        mqttSubscriptionsReady = true;
        Serial.println("[MQTT SUB] Da subscribe classification va uncertain (QoS 1).");
      } else {
        printMqttError("SUB topics", mqttSubscriber, mqttSubscribeNet);
        mqttSubscriber.disconnect();
      }
    } else {
      printMqttError("SUB", mqttSubscriber, mqttSubscribeNet);
    }
    lastMqttSubscribeAttemptMs = millis();
  }
}

void updateIotStatus() {
  if (!mqttPublisher.connected()) return;
  const bool ready = timeReady && actuatorsReady && sensorsReady &&
                     mqttSubscriber.connected() && mqttSubscriptionsReady;
  if (publishedStatusKnown && ready == publishedOnline) return;
  const char *payload = ready ? "{\"status\":\"online\"}" : "{\"status\":\"offline\"}";
  if (mqttPublisher.publish(mqttStatusTopic, payload, true, 1)) {
    publishedOnline = ready;
    publishedStatusKnown = true;
    Serial.printf("[MQTT PUB] Da gui %s: %s\n", ready ? "online" : "offline", mqttStatusTopic.c_str());
  } else {
    printMqttError("PUB status", mqttPublisher, mqttPublishNet);
    // Dong TCP bat thuong de broker van co the phat LWT offline.
    mqttPublishNet.stop();
    publishedStatusKnown = false;
  }
}

bool getUtcTimestamp(char *buffer, size_t bufferSize) {
  const time_t currentTime = time(nullptr);
  if (!timeReady || currentTime < MIN_VALID_TIME) {
    return false;
  }
  struct tm utcTime;
  if (gmtime_r(&currentTime, &utcTime) == nullptr) {
    return false;
  }
  return strftime(buffer, bufferSize, "%Y-%m-%dT%H:%M:%SZ", &utcTime) != 0;
}

void publishFillLevels() {
  if (!timeReady || !mqttPublisher.connected()) return;
  FillReport report;
  if (!takeFillReport(&report)) return;

  for (int i = 0; i < 3; ++i) {
    const FillReading &reading = report.bins[i];
    if (reading.lidUnstable) {
      Serial.printf("[Sensor] Bo qua thung %d: nap dang mo/di chuyen/chua on dinh\n", i + 1);
      continue;
    }
    uint32_t currentLidVersion = 0;
    if (!getClosedLidVersion(i, &currentLidVersion) || currentLidVersion != reading.lidVersion) {
      Serial.printf("[Sensor] Bo qua thung %d: nap da di chuyen sau luc do\n", i + 1);
      continue;
    }
    if (reading.validSamples != FILL_SAMPLES_PER_BIN || !std::isfinite(reading.distanceCm) ||
        reading.distanceCm < 2 || reading.distanceCm > 400) {
      Serial.printf("[Sensor] Loi thung %d: chi %u/%u mau hop le, khong gui so do\n",
                    i + 1, reading.validSamples, FILL_SAMPLES_PER_BIN);
      continue;
    }
    if (millis() - reading.measuredAtMs > FILL_MAX_AGE_MS || reading.measuredAtUtc < MIN_VALID_TIME) {
      Serial.printf("[Sensor] Bo qua thung %d: so do cu hoac chua dong bo NTP\n", i + 1);
      continue;
    }
    struct tm utcTime;
    char timestamp[21];
    if (gmtime_r(&reading.measuredAtUtc, &utcTime) == nullptr ||
        strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", &utcTime) == 0) continue;

    JsonDocument message;
    message["distance_cm"] = roundf(reading.distanceCm * 10.0f) / 10.0f;
    message["timestamp"] = timestamp;
    String payload;
    serializeJson(message, payload);
    // Chi main loop goi MQTT; task cam bien khong truy cap client.
    if (mqttPublisher.publish(mqttFillTopics[i], payload, false, 0)) {
      Serial.printf("[Sensor] Thung %d: TB cat ngon %u mau (bo %u nho, %u lon) = %.1f cm (min %.1f, max %.1f)\n",
                    i + 1, reading.validSamples, FILL_TRIM_LOW, FILL_TRIM_HIGH,
                    reading.distanceCm, reading.minCm, reading.maxCm);
      Serial.print("[Fill] Da gui ");
      Serial.println(mqttFillTopics[i]);
      Serial.println(payload);
    } else {
      printMqttError("PUB fill", mqttPublisher, mqttPublishNet);
    }
  }
}

void printUtcTime() {
  char timestamp[21];
  if (getUtcTimestamp(timestamp, sizeof(timestamp))) {
    Serial.print("[Time] UTC: ");
    Serial.println(timestamp);
  }
}

void updateTime(unsigned long now) {
  if (!ntpStarted || now - lastTimeCheckMs < TIME_CHECK_INTERVAL_MS) {
    return;
  }
  lastTimeCheckMs = now;
  if (!timeReady && time(nullptr) >= MIN_VALID_TIME) {
    timeReady = true;
    Serial.println("[Time] Dong bo NTP thanh cong!");
    printUtcTime();
  }
  if (!timeReady && WiFi.status() == WL_CONNECTED &&
      now - lastNtpWaitReportMs >= NTP_WAIT_REPORT_MS) {
    lastNtpWaitReportMs = now;
    Serial.println("[Time] Chua lay duoc gio NTP. Kiem tra Internet; van dang cho dong bo.");
  }
}

void startWiFi() {
  lastWiFiAttemptMs = millis();
  Serial.println("[WiFi] Dang ket noi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void updateWiFi(unsigned long now) {
  if (!wifiConfigured) {
    return;
  }

  const bool connected = WiFi.status() == WL_CONNECTED;
  if (connected) {
    if (!wifiWasConnected) {
      Serial.println("[WiFi] Ket noi thanh cong!");
      Serial.print("[WiFi] IP: ");
      Serial.println(WiFi.localIP());
      if (!ntpStarted) {
        // UTC: khong cong 7 gio vao timestamp gui MQTT.
        configTime(0, 0, "pool.ntp.org", "time.google.com", "time.nist.gov");
        ntpStarted = true;
        lastNtpWaitReportMs = now;
        Serial.println("[Time] Dang dong bo gio NTP...");
      }
    }
  } else {
    if (wifiWasConnected) {
      Serial.println("[WiFi] Mat ket noi, se tu thu lai.");
    }
    if (now - lastWiFiAttemptMs >= WIFI_RETRY_INTERVAL_MS) {
      Serial.println("[WiFi] Chua ket noi duoc. Kiem tra ten/mat khau va mang Wi-Fi.");
      startWiFi();
    }
  }
  wifiWasConnected = connected;
}

void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.println();
  Serial.println("[IoT] Tuong - Smart Waste");
  Serial.println("[IoT] Khoi dong thanh cong - Wi-Fi, NTP va MQTT/TLS");
  configurationReady = WIFI_SSID[0] != '\0' && strcmp(WIFI_SSID, "DIEN_TEN_WIFI") != 0 &&
      MQTT_HOST[0] != '\0' && strcmp(MQTT_HOST, "DIEN_DIA_CHI_BROKER") != 0 && MQTT_PORT != 0 &&
      MQTT_PUBLISH_USER[0] != '\0' && MQTT_PUBLISH_PASSWORD[0] != '\0' &&
      MQTT_SUBSCRIBE_USER[0] != '\0' && MQTT_SUBSCRIBE_PASSWORD[0] != '\0' &&
      strncmp(MQTT_PUBLISH_USER, "DIEN_", 5) != 0 && strncmp(MQTT_SUBSCRIBE_USER, "DIEN_", 5) != 0 &&
      strncmp(MQTT_PUBLISH_PASSWORD, "DIEN_", 5) != 0 && strncmp(MQTT_SUBSCRIBE_PASSWORD, "DIEN_", 5) != 0 &&
      strcmp(WIFI_PASSWORD, "DIEN_MAT_KHAU_WIFI") != 0;
  if (!configurationReady) {
    Serial.println("[Config] Dien day du cau hinh Wi-Fi/MQTT trong secrets.h roi nap lai.");
    return;
  }
  actuatorsReady = setupActuators();
  if (!actuatorsReady) {
    Serial.println("[Servo] Khoi tao that bai. Kiem tra thu vien/cau hinh va reset de thu lai.");
  }
  sensorsReady = actuatorsReady && setupFillSensors();
  if (!sensorsReady) {
    Serial.println("[Sensor] Khoi tao that bai. Reset de thu lai.");
  }
  setupMqtt();
  Serial.println("[TEST] Sau khi NTP dong bo, gui chu t trong Serial Monitor de test chong mo trung.");

  wifiConfigured = true;
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(false);  // Chu dong thu lai moi 15 giay bang millis().
  startWiFi();
}

void loop() {
  if (!configurationReady) {
    vTaskDelay(pdMS_TO_TICKS(10));
    return;
  }
  const unsigned long now = millis();
  updateWiFi(now);
  updateTime(now);
  updateSerialTest();
  updateMqtt();
  updateIotStatus();
  publishFillLevels();
  const unsigned long reportNow = millis();
  if (reportNow - lastReportMs >= REPORT_INTERVAL_MS) {
    lastReportMs = reportNow;
    Serial.print("[IoT] Dang chay - uptime (giay): ");
    Serial.println(reportNow / 1000UL);
    printUtcTime();
  }
  vTaskDelay(pdMS_TO_TICKS(10));
}
