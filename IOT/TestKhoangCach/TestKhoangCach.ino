// Test rieng: dong nap, moi 3 giay do 1 thung theo thu tu HC -> VC -> TC.
// Moi luot chi do 1 lan, khong loc/trung binh, khong dung Wi-Fi hay MQTT.
#include <Arduino.h>
#include <ESP32Servo.h>

// Thu tu: huu co, vo co, tai che. GPIO theo so do Tuong da cung cap.
const char *TEN_THUNG[] = {"HC - Huu co", "VC - Vo co", "TC - Tai che"};
constexpr int SERVO_PIN[] = {19, 21, 18};
constexpr int TRIG_PIN[] = {14, 27, 13};
constexpr int ECHO_PIN[] = {35, 32, 34};
constexpr unsigned long CHU_KY_MS = 3000;
constexpr unsigned long ECHO_TIMEOUT_US = 25000;

Servo nap[3];
bool napSanSang = true;
unsigned long lanDoTruoc = 0;
int thungHienTai = 0;

void setup() {
  Serial.begin(115200);
  pinMode(25, OUTPUT);  // Tat LED do.
  pinMode(26, OUTPUT);  // Tat LED xanh.
  digitalWrite(25, LOW);
  digitalWrite(26, LOW);

  for (int i = 0; i < 3; ++i) {
    pinMode(TRIG_PIN[i], OUTPUT);
    digitalWrite(TRIG_PIN[i], LOW);
    pinMode(ECHO_PIN[i], INPUT);
    nap[i].setPeriodHertz(50);
    nap[i].attach(SERVO_PIN[i]);
    if (nap[i].attached()) {
      nap[i].write(180);  // Giu nap dong trong suot bai test.
    } else {
      napSanSang = false;
      Serial.printf("[LOI] Khong khoi tao duoc servo %s\n", TEN_THUNG[i]);
    }
  }

  Serial.println("=== TEST KHOANG CACH: HC -> VC -> TC ===");
  Serial.println("Nap dong 180 do. Moi 3 giay do 1 thung, moi thung lap lai sau khoang 9 giay.");
  if (!napSanSang) Serial.println("[LOI] Dung do vi chua dieu khien duoc ca 3 nap. Kiem tra va reset lai.");
  lanDoTruoc = millis();  // Cho 3 giay de nap dong on dinh truoc lan do dau.
}

void loop() {
  const unsigned long bayGio = millis();
  if (!napSanSang || bayGio - lanDoTruoc < CHU_KY_MS) return;
  lanDoTruoc = bayGio;

  const int i = thungHienTai;
  digitalWrite(TRIG_PIN[i], LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN[i], HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN[i], LOW);
  const unsigned long echoUs = pulseIn(ECHO_PIN[i], HIGH, ECHO_TIMEOUT_US);

  Serial.print("[");
  Serial.print(bayGio / 1000UL);
  Serial.print(" s] ");
  Serial.print(TEN_THUNG[i]);
  Serial.print(": ");
  if (echoUs == 0) {
    Serial.println("KHONG NHAN DUOC ECHO - kiem tra cam bien/day/vat can");
  } else {
    const float khoangCachCm = echoUs / 58.0f;
    Serial.print(khoangCachCm, 2);
    Serial.print(" cm");
    if (khoangCachCm < 2.0f || khoangCachCm > 400.0f) {
      Serial.print(" (ngoai vung do 2..400 cm, khong dung de hieu chuan)");
    }
    Serial.println();
  }
  thungHienTai = (thungHienTai + 1) % 3;
  if (thungHienTai == 0) {
    Serial.println("----------------------------------------");
  }
}
