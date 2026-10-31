# IoT - Nguyen Duc Tuong

Phan cung da lap va duoc Tuong xac nhan test hoat dong tot.
Firmware duoc viet va nap bang **Arduino IDE**.

## Cau truc thu muc dang su dung

```text
IOT/
  README.md
  SmartWasteIoT/
    SmartWasteIoT.ino       # Chuong trinh chinh, Wi-Fi, NTP, MQTT, test Serial
    actuator_control.h     # GPIO, goc servo, timer va khai bao ham
    actuator_control.cpp   # Dieu khien servo/LED
    fill_sensors.h         # GPIO cam bien va cau truc so do
    fill_sensors.cpp       # Doc HC-SR04 va loc mau loi
    iot_logic.h           # Kiem tra timestamp, UUID, cache va trung binh cat ngon
    mqtt_ca.h              # Chung chi CA cho MQTT/TLS
    secrets.example.h      # Mau cau hinh de ban giao
    secrets.h              # Cau hinh cuc bo, duoc Git bo qua
  tests/
    iot_logic_test.cpp      # Test logic, khong can cam board
    run_logic_tests.ps1     # Chay test bang MSVC tren Windows
```

File `.ino`, `.cpp` va `.h` tren can nam cung thu muc `SmartWasteIoT`.
Mo file `.ino` trong Arduino IDE de bien dich va nap. Thu muc `firmware/`
va file `platformio.ini` cu chi la cac file rong, da bo vi khong duoc dung.
`build/` la dau ra bien dich, co the tao lai; `.theia/` la cau hinh IDE cuc bo.
Hai thu muc nay duoc Git bo qua, khong can ban giao cung ma nguon.

## Buoc 1 - Tao sketch va kiem tra nap code

1. Trong Arduino IDE, mo File > Preferences. Neu chua co ho tro ESP32,
   them URL sau vao Additional Boards Manager URLs:
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json`.
2. Mo Boards Manager, tim va cai `esp32` cua Espressif Systems.
3. Chon dung board va cong COM trong Tools > Board va Tools > Port.
   Neu board la ESP32-WROOM-32 DevKit thong thuong, co the dung
   `ESP32 Dev Module`; cac dong S3/C3 can chon dung board tuong ung.
4. Mo `SmartWasteIoT/SmartWasteIoT.ino` bang File > Open.
5. Bam Verify, sau do Upload.
6. Mo Serial Monitor o **115200 baud**. Bam EN/RESET neu muon xem lai
   thong bao khoi dong. Ban hien tai in uptime moi 10 giay.

Sketch hien tai da duoc nang cap sang buoc 6 (them HC-SR04 va gui khoang cach); log uptime van giu
de kiem tra vong lap dang chay.

Thu vien chuan bi cho cac buoc tiep theo (cai bang Library Manager):

- ESP32Servo: dieu khien servo ESP32.
- ArduinoJson 7 cua Benoit Blanchon: xu ly JSON.
- MQTT cua Joel Gaehwiler (256dpi/arduino-mqtt): MQTT, ho tro QoS 1.

Sketch hien tai can ca ba thu vien tren: MQTT, ArduinoJson 7 va ESP32Servo.

## Buoc 2 - Ket noi Wi-Fi

1. Mo `SmartWasteIoT/SmartWasteIoT.ino` trong Arduino IDE.
2. Mo tab `secrets.h`, dien ten Wi-Fi va mat khau trong dau ngoac kep.
   Neu vua clone repo va chua co file nay, sao chep `secrets.example.h`
   thanh `secrets.h` trong cung thu muc sketch.
3. Luu tat ca, chon dung board/COM va Upload lai.
4. Mo Serial Monitor 115200 baud, bam EN/RESET neu can.
5. Ket qua dat: `[WiFi] Ket noi thanh cong!` va `[WiFi] IP: ...`.
6. Thu tat/bat mang Wi-Fi: thiet bi se thu lai moi 15 giay,
   log uptime van tiep tuc. Ket noi thanh cong se in lai IP.

Thu vien `WiFi.h` di kem goi board ESP32. Chuong trinh dung che do
station, khong dung vong while cho ket noi hoac delay keo dai.
Khong in mat khau ra Serial. `secrets.h` da duoc bo qua boi Git.
Khi mang chua ket noi, kiem tra lai ten, mat khau va cau hinh mang.

Tham chieu: [Wi-Fi API Espressif](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/wifi.html).

## Buoc 3 - Dong bo thoi gian NTP

1. Giu nguyen thong tin Wi-Fi da ket noi thanh cong trong `secrets.h`.
2. Mo lai sketch trong Arduino IDE de tai noi dung moi, Verify va Upload.
3. Mo Serial Monitor 115200 baud va bam EN/RESET.
4. Sau khi Wi-Fi ket noi, chuong trinh tu goi `configTime(0, 0, ...)`
   voi `pool.ntp.org`, `time.google.com`, `time.nist.gov`.
5. Ket qua dat: `[Time] Dong bo NTP thanh cong!` va dong
   `[Time] UTC: YYYY-MM-DDTHH:MM:SSZ` co ngay gio thuc te dung.
6. UTC cham hon gio Viet Nam 7 tieng; khong sua cong 7 gio vao payload MQTT.

Chu ky log uptime va UTC la 10 giay de de doc Serial. Viec doi gio chay
nen, khong co vong while/delay cho NTP. Khi chua co gio hop le,
`getUtcTimestamp()` tra false, khong sinh timestamp nam 1970.
Neu sau 30 giay van chua dong bo, Serial nhac kiem tra Internet;
Wi-Fi va vong lap van tiep tuc hoat dong. Khi mat Wi-Fi sau dong bo,
dong ho he thong van chay; reset nguon thi can dong bo lai.
MQTT chi bat dau sau khi buoc NTP thanh cong.

Tham chieu: [Vi du SimpleTime cua Espressif](https://github.com/espressif/arduino-esp32/blob/master/libraries/ESP32/examples/Time/SimpleTime/SimpleTime.ino).

## Buoc 4 - MQTT qua TLS

1. Library Manager: tim `MQTT` (hoac `lwmqtt`), cai **MQTT cua Joel Gaehwiler**
   tu du an 256dpi/arduino-mqtt. Thu vien cung cap header `MQTT.h`.
2. Trong `secrets.h` dien host, port, tai khoan publish va subscribe.
   File mau `secrets.example.h` liet ke cac truong can co.
   Wi-Fi da test duoc giu nguyen. `AREA_NUMBER = 1` la khu vuc test mac dinh.
3. CA trong `mqtt_ca.h` la DigiCert Global Root CA theo vi du Serverless
   cua EMQX. ESP32 xac minh chung chi, khong tat kiem tra TLS.
   Neu deployment dung CA khac, thay bang CA tu trang Overview cua deployment.
4. Mo lai sketch, Verify, Upload, mo Serial Monitor 115200 baud, reset.
5. Sau Wi-Fi/NTP, can thay PUB va SUB ket noi, subscribe classification va
   uncertain thanh cong, sau do gui online. Co the thay offline ngan luc
   PUB da ket noi nhung SUB chua san sang.

Hai tai khoan test do Tuong cung cap duoc dung tren **hai MQTT client**,
moi client mot ket noi TLS va client ID rieng theo khu vuc + ma chip.
PUB gui `school/area1/status/iot` online QoS 1 retain=true;
LWT offline cung topic/QoS/retain. SUB nhan hai topic:

```
school/area1/classification
school/area1/uncertain
```

MQTTX test:

1. Ket noi bang tai khoan subscribe va subscribe `school/area1/status/iot`
   QoS 1: phai thay `{"status":"online"}` (co retain).
2. Tu connection publish, gui `{"timestamp":"2026-10-31T02:18:01Z"}`
   len `school/area1/uncertain`, QoS 1, **retain=false**.
3. Serial ESP32 phai in `[MQTT RX] school/area1/uncertain` va payload.
4. Co the gui classification dung hop dong de kiem tra nhan; neu Backend
   dang chay, tin nay co the tao log that. Test uncertain truoc la du.

Tu buoc 5, tin classification/uncertain hop le se kich hoat servo/LED.
Tu buoc 6, chuong trinh gui so do HC-SR04 that; khong gui du lieu gia.
Tai khoan co ten publish/subscribe chua chung minh quyen ACL; can doi chieu
log thuc te va quyen topic tren broker neu bi tu choi.
SUB va PUB co trang thai ket noi rieng. Status IoT chi gui online khi PUB,
SUB va hai subscription san sang, co gio NTP va khoi tao thanh cong hai
task phan cung. Neu SUB mat ket noi, PUB se gui offline; khi PUB mat ket
noi bat thuong, broker phat LWT offline. Online khong chung minh servo
thuc te da quay hay cam bien do dung, vi mo hinh khong co phan hoi vi tri.

Moi client thu lai theo chu ky 15 giay khi Wi-Fi va gio hop le. Thu vien
MQTT/TLS dung loi goi dong bo, mot lan ket noi co the tam dung loop trong
vai giay. Tu buoc 5, timer servo/LED chay trong task FreeRTOS rieng de
khong phu thuoc thoi gian doi mang trong loop.
Log loi co `lastError`, `returnCode` va thong tin TLS neu co.
Khong in mat khau ra Serial.

Tham chieu:
- [MQTT library va API](https://github.com/256dpi/arduino-mqtt)
- [EMQX Cloud ESP32 TLS](https://docs.emqx.com/en/cloud/latest/connect_to_deployments/esp32.html)

## Buoc 5 - Servo va LED theo ket qua AI

Tuong da xac nhan tat ca servo: **dong 180 do, mo 100 do**.
Khai bao trong `actuator_control.h`: chan, goc rieng tung servo,
`LID_OPEN_MS = 5000` va `LED_ON_MS = 5000`.

1. Cai ArduinoJson **ban 7** cua Benoit Blanchon va ESP32Servo neu chua co.
2. Mo lai sketch, Verify, Upload. Arduino tu bien dich file
   `actuator_control.cpp` trong cung thu muc sketch.
3. Sau reset, ba servo duoc dua ve goc dong 180, hai LED tat.
4. Ket noi MQTTX bang tai khoan publish, gui classification theo bang duoi,
   QoS 1, **retain=false**. Neu AI that dang chay, tam dung AI khi test
   bang tay de tranh nhan xen ke lenh that.

| waste_type | Servo | Goc mo / dong | LED |
| --- | --- | --- | --- |
| recyclable | GPIO18 | 100 / 180 | Xanh GPIO26 |
| organic | GPIO19 | 100 / 180 | Xanh GPIO26 |
| inorganic | GPIO21 | 100 / 180 | Xanh GPIO26 |

Vi du topic `school/area1/classification`:

```json
{
  "log_id": "11111111-1111-4111-8111-111111111111",
  "waste_type": "organic",
  "confidence": 0.9,
  "timestamp": "2026-10-31T02:30:00Z"
}
```

Dung timestamp UTC thuc te khi test. Tin classification co the tao log
tren Backend. Moi luot test moi can doi `log_id` thanh UUID moi.

Ket qua: servo huu co mo 100 do, LED xanh bat; sau khoang 5 giay servo
dong 180 do, LED tat. Gui lai cung `log_id`: Serial bao bo qua, khong mo lai.
Cache nho 32 log_id gan nhat trong RAM, mat khi reset; khong phai luu ben vung.

Test `school/area1/uncertain` voi payload co `timestamp`:
LED do GPIO25 bat 5 giay, khong mo them nap. Neu nap da mo tu lenh truoc,
nap do van dong theo timer cu. LED do/xanh co timer doc lap.
Lenh classification moi khac log_id cung thung se tinh lai 5 giay mo cho thung do.
Lenh cho thung khac khong dong ep thung dang mo.

Firmware kiem tra JSON object, timestamp ISO UTC hop le, UUID dung hinh
thuc, loai rac hop le va confidence la so huu han trong 0..1.
Timestamp chap nhan `Z` hoac `+00:00`, voi phan thap phan tuy chon.
Lenh cu qua 30 giay hoac som hon dong ho ESP qua 5 giay bi bo qua.
Khi test bang tay, can thay timestamp vi du bang gio UTC hien tai;
khong copy nguyen timestamp cu. Ben gui van phai dung retain=false.
Thu vien MQTT hien tai khong dua co retained vao callback ung dung;
kiem tra tuoi tin nhan khong thay the hoan toan viec tat retain o ben gui.
Lenh duoc dua vao queue 8 phan tu, task servo/LED xu ly doc lap voi mang.
Neu queue day hoac lenh cho trong queue qua 2 giay, lenh bi bo qua va co log.
Khi mat Wi-Fi luc dang mo,
timer servo van dong nap; co the test bang cach tat diem phat Wi-Fi.

Serial mong doi cho huu co:

```text
[Servo] Mo organic: 100 do, tu dong sau 5000 ms
[LED] Bat xanh
[Servo] Dong organic: 180 do
[LED] Tat xanh
```

Dung nguon on dinh cho mo hinh: truoc do Tuong da gap brownout khi bat Wi-Fi.
Ket qua goc thuc te phu thuoc khoang xung servo da hieu chinh; hien dung
`attach(pin)` mac dinh cua ESP32Servo. Neu code test cu dung min/max xung
khac thi can dung lai dung gia tri do.

## Test chong mo trung de hon: chi can Serial Monitor

1. Nap ban sketch moi, mo Serial Monitor 115200 baud, cho NTP dong bo.
2. Tam dung AI de khong xen ke lenh phan loai that trong luc test.
3. Go chu `t` vao o gui cua Serial Monitor, bam Enter hoac Send.
4. Nap huu co mo 100 do va dong 180 do sau 5 giay.
5. Sau khoang 6,5 giay, sketch tu xu ly lai cung log_id. Can thay
   `[MQTT] Bo qua log_id trung, khong mo lai nap`; nap khong mo lan hai.
6. Moi lan gui `t` tao mot UUID test moi; co the test lai khong can reset.

Tin test di truc tiep qua cung ham xu ly JSON/UUID/queue voi tin MQTT that,
khong publish len broker va khong tao log gia tren Backend. Cach nay kiem
tra logic chong trung tren ESP32 va hanh dong thuc te, khong kiem tra
viec broker giao lap goi QoS 1. Doi chieu log `[TEST]` de nhan ra tin noi bo.

## Buoc 6 - Do khoang cach va gui MQTT

Firmware dung `fill_sensors.h/.cpp` trong cung thu muc sketch, khong can
thu vien cam bien bo sung. Thu tu dang cau hinh:

| Thung | Trig | Echo | Topic (area1) |
| --- | --- | --- | --- |
| Tai che | 13 | 34 | school/area1/fill_level/recyclable |
| Huu co | 14 | 35 | school/area1/fill_level/organic |
| Vo co | 27 | 32 | school/area1/fill_level/inorganic |

1. Mo lai sketch trong Arduino IDE, Verify va Upload nhu cac buoc truoc.
2. De nap dong, cam bien huong vao day thung/mat rac va cho Wi-Fi, NTP,
   MQTT PUB ket noi. Mo Serial Monitor 115200 baud.
3. Moi chu ky khoang **7 giay**, task cam bien doc tung thung, **10 mau/thung**,
   thoi diem bat dau cac lan do cach nhau khoang **70ms**.
   Ba cam bien doc lan luot, khong phat sieu am dong thoi. Moi thung chiem
   khoang 0,7 giay (gom nghi sau mau cuoi); ca ba thung khoang 2,1 giay.
   Bao cao duoc gui sau khi hoan tat lay mau ca ba thung.
   `FILL_INTERVAL_MS = 7000` trong `fill_sensors.h`: binh thuong moi ESP
   gui 3 tin khoang moi 7 giay (mot tin/thung), khong gui tung mau le.
   Day la chu ky gan dung, co the tre khi mang ban hoac bo qua so do loi/nap mo.
4. Moi lan do co timeout Echo 25ms. Bo mau khong phan hoi hoac ngoai
   khoang 2..400cm theo datasheet. Chi khi **du 10/10 mau hop le** moi sap
   xep tang dan, bo **3 mau nho nhat** va **1 mau lon nhat**, sau do lay
   trung binh 6 mau con lai:
   `distance_cm = (mau_thu_4 + ... + mau_thu_9) / 6`.
   Neu thieu mau thi bo dot do cua thung do.
5. Nap dang mo, di chuyen trong/sau dot lay mau hoac vua dong chua du 500ms:
   bo so do cua thung do. Chu ky sau se thu lai. Thoi gian 500ms duoc
   tinh theo lenh servo, chua co cam bien xac nhan vi tri nap thuc te.
6. Main loop gui trung binh cat ngon `distance_cm` lam tron 1 chu so thap phan, cung
   timestamp UTC cua lan do cuoi tung thung, QoS 0 va retain=false.
   So mau va khoang cach lan do duoc cau hinh trong `fill_sensors.h`:
   `FILL_SAMPLES_PER_BIN = 10`, `FILL_SAMPLE_INTERVAL_MS = 70`.
   So mau bo duoc cau hinh boi `FILL_TRIM_LOW = 3`, `FILL_TRIM_HIGH = 1`.
   Log `[Sensor] Thung ...: TB cat ngon 10 mau (bo 3 nho, 1 lon) = ... cm ...`
   giup thay do phan tan cua 10 mau. Khong gioi han so do theo chieu cao thung.
7. Task cam bien chi giu bao cao moi nhat. Khi mat mang khong tich hang doi;
   so do cu qua 20 giay hoac truoc khi co gio NTP hop le se khong duoc gui.

Vi du log (so do thuc te se khac):

```text
[Fill] Da gui school/area1/fill_level/organic
{"distance_cm":12.5,"timestamp":"2026-10-31T02:45:00Z"}
```

`Da gui` cho biet thu vien MQTT da ghi goi QoS 0, chua phai xac nhan
Backend nhan. Dung MQTTX tai khoan subscribe, subscribe
`school/area1/fill_level/+` QoS 0 de kiem tra broker nhan dung 3 topic.
Dat vat o cac do cao khac nhau tung thung va doi chieu dung thung doi so do.
Sau do mo Dashboard: phan tram do Backend tinh tu `height_cm`, khong tinh
tren ESP32. Tai khoan PUB phai co quyen publish cac topic fill_level.

Log `[Sensor] Loi thung ...` nghia la chua du mau hop le, khong gui gia tri 0
de tranh Backend hieu nham thung day. Kiem tra dung thung/day noi, huong
cam bien va vat nam trong khoang do. Log nap chua on dinh co the binh thuong
ngay sau reset hoac khi dang phan loai.

Can Tuong xac nhan cam bien 1/2/3 thuc te lan luot la tai che/huu co/vo co.
Neu khac, sua cap Trig/Echo trong `fill_sensors.h` de giu topic dung thung.
Khi do thung rong, ghi lai khoang cach tung thung va gui Anh cap nhat
`height_cm`; seed Backend dang la gia tri mau, khong thay the so do thuc te.

Tham chieu: [Datasheet HC-SR04](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf).

## So do GPIO da xac nhan

| Thiet bi | GPIO |
| --- | --- |
| Servo tai che | 18 |
| Servo huu co | 19 |
| Servo vo co | 21 |
| HC-SR04 so 1: Trig / Echo | 13 / 34 |
| HC-SR04 so 2: Trig / Echo | 14 / 35 |
| HC-SR04 so 3: Trig / Echo | 27 / 32 |
| LED do / xanh | 25 / 26 |

Echo moi cam bien qua dien tro 1k ohm den GPIO; tu GPIO qua 2k ohm xuong
GND, theo bang dau noi Tuong cung cap. LED vang khong noi.
Thu tu cam bien tam hieu la tai che, huu co, vo co; can doi chieu lai
voi vi tri lap thuc te khi viet phan doc cam bien.

## Nap cho hai khu vuc

Moi vi tri co 1 ESP32 dieu khien 3 ngan (tai che, huu co, vo co), tong 6 ngan.
Dung chung sketch neu dau noi giong nhau. Trong `secrets.h`, dat
`AREA_NUMBER = 1` roi Upload vao COM cua ESP thu nhat; doi thanh
`AREA_NUMBER = 2` roi Upload vao COM cua ESP thu hai. Doi file tren may
khong doi code da luu tren ESP thu nhat. Log khoi dong in khu vuc va client
ID de doi chieu. Khong nap ca hai ESP vao cung khu vuc neu do la hai bo
doc lap, vi so do va lenh se di chung topic.

## Kiem tra va gioi han

Test logic tren Windows (can MSVC C++ Build Tools):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File IOT/tests/run_logic_tests.ps1
```

Lenh chi ap dung ExecutionPolicy cho tien trinh test, khong doi chinh sach
he thong. Test dung truc tiep `iot_logic.h` cua firmware, khong ket noi
broker, khong nap board; bao gom UTC/leap day/tin cu, cache UUID,
mau loi/NaN/thieu mau, trung binh cat ngon, gioi han bo mau va quay vong millis.
File bien dich test o thu muc tam.

Kiem thu thuc te sau moi lan nap ban moi:

- Ca hai bo nhan dung khu vuc, moi loai rac mo dung nap, dong sau 5 giay.
- Tin uncertain bat LED do; lenh test `t` khong mo lai cung log_id.
- Rut/mat Wi-Fi khi nap dang mo: nap van dong, status offline va tu
  online lai khi ca hai ket noi MQTT duoc khoi phuc.
- Giu bia phang va dung thuoc de doi chieu so do trung binh cat ngon/min/max.
- Chay nhieu luot servo va Wi-Fi dong thoi de xac nhan khong brownout.

Chieu cao thung va phep tinh % nam o Backend. Khong the tu code xac nhan
database da hieu chuan hay nguon cap, vi tri cam bien va co cau nap da on.
Khong tat brownout detector de che loi nguon. Cache UUID 32 phan tu van
nam trong RAM va mat khi reset; gioi han tuoi lenh giam nguy co xu ly tin
cu nhung khong la luu lich su chong trung ben vung.

## Tai lieu tham chieu

- [Cai dat ESP32 cho Arduino IDE](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html)
- [ESP32Servo](https://github.com/madhephaestus/ESP32Servo)
- [ArduinoJson](https://arduinojson.org/v7/how-to/install-arduinojson/)
- [MQTT](https://github.com/256dpi/arduino-mqtt)
- [Hop dong MQTT cua du an](../DOCS/06-mqtt/mqtt-topic-va-json-format.md)
