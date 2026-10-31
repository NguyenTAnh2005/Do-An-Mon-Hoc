#pragma once

#include <cmath>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

// Logic thuan C++, dung chung cho firmware va test tren may tinh.
namespace iot {
inline bool isUuid(const char *value) {
  if (value == nullptr || strlen(value) != 36) return false;
  for (size_t i = 0; i < 36; ++i) {
    if (i == 8 || i == 13 || i == 18 || i == 23) {
      if (value[i] != '-') return false;
    } else if (!((value[i] >= '0' && value[i] <= '9') ||
                 (value[i] >= 'a' && value[i] <= 'f') ||
                 (value[i] >= 'A' && value[i] <= 'F'))) return false;
  }
  return true;
}

inline char lowerHex(char value) {
  return value >= 'A' && value <= 'F' ? static_cast<char>(value + ('a' - 'A')) : value;
}

template <size_t Capacity>
class RecentLogIds {
  static_assert(Capacity > 0, "UUID cache cannot be empty");
  char ids[Capacity][37] = {};
  size_t next = 0;

 public:
  bool contains(const char *id) const {
    if (!isUuid(id)) return false;
    for (size_t i = 0; i < Capacity; ++i) {
      bool equal = true;
      for (size_t j = 0; j < 36; ++j) {
        if (ids[i][j] != lowerHex(id[j])) { equal = false; break; }
      }
      if (equal) return true;
    }
    return false;
  }

  bool remember(const char *id) {
    if (!isUuid(id)) return false;
    if (contains(id)) return true;
    for (size_t j = 0; j < 36; ++j) ids[next][j] = lowerHex(id[j]);
    ids[next][36] = '\0';
    next = (next + 1) % Capacity;
    return true;
  }
};

inline bool parseUtcTimestamp(const char *text, int64_t &epoch) {
  if (text == nullptr) return false;
  const size_t length = strlen(text);
  if (length < 20 || length > 35) return false;
  if (text[4] != '-' || text[7] != '-' || text[10] != 'T' ||
      text[13] != ':' || text[16] != ':') return false;
  for (size_t i = 0; i < 19; ++i) {
    if (i == 4 || i == 7 || i == 10 || i == 13 || i == 16) continue;
    if (text[i] < '0' || text[i] > '9') return false;
  }
  const int year = (text[0] - '0') * 1000 + (text[1] - '0') * 100 +
                   (text[2] - '0') * 10 + text[3] - '0';
  const int month = (text[5] - '0') * 10 + text[6] - '0';
  const int day = (text[8] - '0') * 10 + text[9] - '0';
  const int hour = (text[11] - '0') * 10 + text[12] - '0';
  const int minute = (text[14] - '0') * 10 + text[15] - '0';
  const int second = (text[17] - '0') * 10 + text[18] - '0';
  if (year < 1970 || month < 1 || month > 12 || hour > 23 || minute > 59 || second > 59) return false;
  const bool leap = year % 4 == 0 && (year % 100 != 0 || year % 400 == 0);
  const int daysPerMonth[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  if (day < 1 || day > daysPerMonth[month - 1] + (month == 2 && leap ? 1 : 0)) return false;

  size_t position = 19;
  if (text[position] == '.') {
    const size_t fractionStart = ++position;
    while (text[position] >= '0' && text[position] <= '9') ++position;
    if (position == fractionStart || position - fractionStart > 9) return false;
  }
  // Hop dong dung UTC: chap nhan Z hoac +00:00, ke ca microseconds tu Python.
  if (strcmp(text + position, "Z") != 0 && strcmp(text + position, "+00:00") != 0) return false;

  const int previousYear = year - 1;
  int64_t days = 365LL * (year - 1970) + previousYear / 4 - previousYear / 100 +
                 previousYear / 400 - (1969 / 4 - 1969 / 100 + 1969 / 400);
  for (int m = 1; m < month; ++m) days += daysPerMonth[m - 1] + (m == 2 && leap ? 1 : 0);
  days += day - 1;
  epoch = days * 86400 + hour * 3600 + minute * 60 + second;
  return true;
}

inline bool isFreshTimestamp(const char *text, int64_t now,
                             int64_t maxAgeSeconds = 30, int64_t futureToleranceSeconds = 5) {
  int64_t epoch = 0;
  if (maxAgeSeconds < 0 || futureToleranceSeconds < 0 || !parseUtcTimestamp(text, epoch)) return false;
  return epoch >= now - maxAgeSeconds && epoch <= now + futureToleranceSeconds;
}

inline bool elapsed(uint32_t now, uint32_t since, uint32_t interval) {
  return static_cast<uint32_t>(now - since) >= interval;
}

template <size_t Capacity>
struct DistanceSamples {
  static_assert(Capacity > 0, "Sample buffer cannot be empty");
  unsigned int count = 0;
  float minCm = 400;
  float maxCm = 2;

 private:
  float sorted[Capacity] = {};

 public:
  bool add(float cm) {
    if (!std::isfinite(cm) || cm < 2 || cm > 400 || count >= Capacity) return false;
    size_t position = count;
    while (position > 0 && sorted[position - 1] > cm) {
      sorted[position] = sorted[position - 1];
      --position;
    }
    sorted[position] = cm;
    ++count;
    if (cm < minCm) minCm = cm;
    if (cm > maxCm) maxCm = cm;
    return true;
  }

  float trimmedMean(size_t trimLow, size_t trimHigh) const {
    if (count != Capacity || trimLow >= Capacity || trimHigh >= Capacity - trimLow) return -1.0f;
    float sum = 0;
    const size_t end = Capacity - trimHigh;
    for (size_t i = trimLow; i < end; ++i) sum += sorted[i];
    return sum / static_cast<float>(end - trimLow);
  }
};
}  // namespace iot
