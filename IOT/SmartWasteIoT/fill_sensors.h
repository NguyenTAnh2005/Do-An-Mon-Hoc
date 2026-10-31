#pragma once
#include <stdint.h>
#include <time.h>

// Thu tu: tai che, huu co, vo co. Doi tai day neu lap khac thu tu.
constexpr int SENSOR_TRIG_PINS[3] = {13, 14, 27};
constexpr int SENSOR_ECHO_PINS[3] = {34, 35, 32};
constexpr unsigned int FILL_SAMPLES_PER_BIN = 10;
constexpr unsigned long FILL_SAMPLE_INTERVAL_MS = 70;
constexpr unsigned int FILL_TRIM_LOW = 3;
constexpr unsigned int FILL_TRIM_HIGH = 1;
constexpr unsigned long FILL_INTERVAL_MS = 7000;
constexpr unsigned long FILL_MAX_AGE_MS = 20000;

struct FillReading {
  float distanceCm;
  float minCm;
  float maxCm;
  unsigned int validSamples;
  bool lidUnstable;
  uint32_t lidVersion;
  unsigned long measuredAtMs;
  time_t measuredAtUtc;
};

struct FillReport {
  FillReading bins[3];
};

bool setupFillSensors();
bool takeFillReport(FillReport *report);
