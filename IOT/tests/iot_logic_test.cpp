#include <cstdio>
#include <limits>
#include "../SmartWasteIoT/iot_logic.h"

namespace {
int checks = 0;
int failures = 0;
void check(bool passed, const char *name) {
  ++checks;
  if (!passed) { ++failures; std::printf("FAIL: %s\n", name); }
}
}

int main() {
  int64_t epoch = -1;
  check(iot::parseUtcTimestamp("1970-01-01T00:00:00Z", epoch) && epoch == 0, "Unix epoch");
  check(iot::parseUtcTimestamp("2000-02-29T00:00:00Z", epoch) && epoch == 951782400, "Gregorian leap day");
  check(iot::parseUtcTimestamp("2026-10-31T02:41:16.241360Z", epoch) && epoch == 1793414476, "AI microsecond timestamp");
  check(iot::parseUtcTimestamp("2026-10-31T02:41:16+00:00", epoch) && epoch == 1793414476, "Python UTC offset");
  check(iot::parseUtcTimestamp("2026-10-31T02:41:16.123456789+00:00", epoch), "Nanosecond fraction with UTC offset");
  check(!iot::parseUtcTimestamp(nullptr, epoch), "Null timestamp");
  check(!iot::parseUtcTimestamp("", epoch), "Empty timestamp");
  check(!iot::parseUtcTimestamp("2026-02-29T00:00:00Z", epoch), "Reject invalid leap day");
  check(!iot::parseUtcTimestamp("2100-02-29T00:00:00Z", epoch), "Century is not a leap year");
  check(!iot::parseUtcTimestamp("2026-04-31T00:00:00Z", epoch), "Reject nonexistent day");
  check(!iot::parseUtcTimestamp("2026-10-31T24:00:00Z", epoch), "Reject hour 24");
  check(!iot::parseUtcTimestamp("2026-10-31T02:60:00Z", epoch), "Reject minute 60");
  check(!iot::parseUtcTimestamp("2026-10-31T02:41:60Z", epoch), "Reject invalid second");
  check(!iot::parseUtcTimestamp("2026-10-31T02:41:16", epoch), "Require timezone");
  check(!iot::parseUtcTimestamp("2026-10-31T02:41:16+07:00", epoch), "Require UTC as contracted");
  check(!iot::parseUtcTimestamp("2026-10-31T02:41:16.Z", epoch), "Reject empty fractional part");
  check(!iot::parseUtcTimestamp("2026-10-31T02:41:16Zjunk", epoch), "Reject trailing garbage");
  check(!iot::parseUtcTimestamp("2026-00-31T02:41:16Z", epoch), "Reject month zero");
  check(!iot::parseUtcTimestamp("2026-10-00T02:41:16Z", epoch), "Reject day zero");
  const char *timestamp = "2026-10-31T02:41:16Z";
  check(iot::isFreshTimestamp(timestamp, 1793414506), "Accept 30 second boundary");
  check(!iot::isFreshTimestamp(timestamp, 1793414507), "Reject delayed command");
  check(iot::isFreshTimestamp(timestamp, 1793414471), "Accept 5 second clock skew");
  check(!iot::isFreshTimestamp(timestamp, 1793414470), "Reject future command");

  const char *a = "abcdefab-1234-4567-89ab-0123456789ab";
  const char *upperA = "ABCDEFAB-1234-4567-89AB-0123456789AB";
  const char *b = "11111111-1111-4111-8111-111111111111";
  const char *c = "22222222-2222-4222-8222-222222222222";
  check(iot::isUuid(a), "Valid UUID");
  check(!iot::isUuid("abcdefab-1234-4567-89ab-0123456789ag"), "Reject nonhex UUID");
  check(!iot::isUuid(nullptr), "Reject null UUID");
  iot::RecentLogIds<2> cache;
  check(!cache.contains(a), "Empty cache");
  check(cache.remember(a) && cache.contains(upperA), "UUID dedup ignores case");
  cache.remember(b);
  cache.remember(upperA);
  check(cache.contains(b), "Duplicate does not consume cache slot");
  cache.remember(c);
  check(!cache.contains(a) && cache.contains(b) && cache.contains(c), "Bounded cache eviction");
  check(!cache.remember("bad-id"), "Do not remember invalid UUID");

  iot::DistanceSamples<10> samples;
  const float unsorted[] = {13, 12, 11, 10, 9, 14, 15, 16, 2};
  for (float cm : unsorted) samples.add(cm);
  check(samples.trimmedMean(3, 1) < 0, "Nine samples are not a complete ten sample batch");
  check(!samples.add(-1) && !samples.add(0) && !samples.add(401), "Reject timeout and out of range");
  check(!samples.add(std::numeric_limits<float>::quiet_NaN()), "Reject NaN sample");
  check(!samples.add(std::numeric_limits<float>::infinity()), "Reject infinity sample");
  check(samples.count == 9 && samples.trimmedMean(3, 1) < 0, "Invalid samples cannot complete a batch");
  samples.add(400);
  check(samples.trimmedMean(3, 1) == 13.5f && samples.minCm == 2 && samples.maxCm == 400,
        "Remove three smallest and one largest, average six retained samples");
  check(samples.trimmedMean(1, 3) == 11.5f, "Low and high trims must not be reversed");
  check(!samples.add(20) && samples.count == 10 && samples.trimmedMean(3, 1) == 13.5f, "Full buffer cannot overflow");
  check(samples.trimmedMean(10, 0) < 0 && samples.trimmedMean(3, 7) < 0, "Reject trimming every sample");
  check(samples.trimmedMean(0, SIZE_MAX) < 0 && samples.trimmedMean(SIZE_MAX, 0) < 0, "Reject overflowing trim counts");
  iot::DistanceSamples<10> identical;
  for (int i = 0; i < 10; ++i) identical.add(12.5f);
  check(identical.trimmedMean(3, 1) == 12.5f, "Repeated values");
  iot::DistanceSamples<5> odd;
  const float oddValues[] = {5, 2, 8, 10, 7};
  for (float cm : oddValues) odd.add(cm);
  check(odd.trimmedMean(1, 1) == 20.0f / 3.0f, "Generic trimmed mean on odd sized batch");
  iot::DistanceSamples<1> single;
  check(single.trimmedMean(0, 0) < 0, "Empty batch has no result");
  single.add(20);
  check(single.trimmedMean(0, 0) == 20, "Single element without trimming");
  check(!iot::elapsed(1999, 0, 2000) && iot::elapsed(2000, 0, 2000), "Queue expiration boundary");
  check(!iot::elapsed(10, UINT32_MAX - 10, 22) && iot::elapsed(10, UINT32_MAX - 10, 21), "millis rollover");
  std::printf("%d checks, %d failures\n", checks, failures);
  return failures == 0 ? 0 : 1;
}
