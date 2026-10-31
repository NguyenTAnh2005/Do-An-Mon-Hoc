#pragma once
#include <stdint.h>

// Cau hinh theo so do va goc servo Tuong da test.
constexpr int SERVO_PINS[3] = {18, 19, 21};
constexpr int SERVO_CLOSED_ANGLES[3] = {180, 180, 180};
constexpr int SERVO_OPEN_ANGLES[3] = {100, 100, 100};
constexpr int LED_RED_PIN = 25;
constexpr int LED_GREEN_PIN = 26;
constexpr unsigned long LID_OPEN_MS = 5000;
constexpr unsigned long LED_ON_MS = 5000;
constexpr unsigned long LID_SETTLE_MS = 500;
constexpr unsigned long ACTUATOR_QUEUE_MAX_AGE_MS = 2000;

bool setupActuators();
// 0=tai che, 1=huu co, 2=vo co, -1=uncertain (chi LED do).
bool queueActuatorCommand(int binIndex);
// Chi do khi nap dong va da on dinh 500ms; version doi moi lan nap di chuyen.
bool getClosedLidVersion(int binIndex, uint32_t *version);
