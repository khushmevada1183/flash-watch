# FLASH watch: BLE protocol (from the decompiled boAt Wearables APK)

Source: `com.boAt.wristgear` v3.5.4 ("boAt Wearables"), decompiled with jadx 1.5.1.
The watch side lives in the bundled CE SDK, package `ce.com.cenewbluesdk`. Paths below are relative
to `sources/` in the jadx output. The decompiled code and the APK are **not** in this repo (they are
boAt's / the SDK vendor's); this file is the protocol as read from them, plus what the real watch did.

Legend: ✅ tested on the real watch · 📖 read from code only, not tested · ⛔ never send

---

## 1. The device

| | |
|---|---|
| Name | `FLASH` |
| MAC | `08:7C:85:03:12:0F` (public) |
| BLE appearance | `0x00C1` (watch) |
| Manufacturer data | key `0xFFFF`, value `0d 11 a9 00 0f 12 03 85 7c 08` (`a9` = devType 169, then MAC reversed) |
| Firmware (from devinfo) ✅ | `169.51.2.8.0` (customer 169, hardware 51, code 2, picture 8, font 0) |
| SDK | CE "K6" protocol, `CEDevK6Proxy`, `CEProtocolB` |

GATT:

| Service / char | Props | Role |
|---|---|---|
| `0x1801` / `0x2A05` | indicate | standard Service Changed |
| **`0xF618`** (`0000f618-0000-1000-8000-00805f9b34fb`) | | the only app service |
| ↳ **`0xB002`** | write, write-without-response | phone → watch |
| ↳ **`0xB001`** | notify | watch → phone |

Where it comes from:
- `proxy/CEDevK6Proxy.java:47`: `UUID = "0000f618-0000-1000-8000-00805f9b34fb"`
- `scan/CEScanDev_4_Android5.java:98`: scan filter on service UUID `F618`
- `bluetooth/a.java:385-400`: on the F618 service, the char with properties `== 16` (notify) is the RX
  channel; every other char goes into the write list. `:130` requests MTU 512; `:186` copies the
  negotiated MTU into `CEProtocolB.MTU`. `:629` plain `writeCharacteristic` (write **with** response).
- No pairing, bonding, encryption or auth token is needed for commands. ✅

---

## 2. Framing (`queue/CEProtocolB.java`)

Everything is cut into 20-byte pages (`slDataL = 20`). No checksum (CRC field is always 0,
`CEDevData.figureCrc16()` returns 0).

**Head page (index 0)**
```
[0]     0x00            page index 0 = head
[1]     devType         phone sends 1 (CEDevK6Proxy.devType = 1, PID_618); watch sends 0xA9
[2]     pages           number of follow-up pages = ceil((len-10)/19), capped at 255 (except type 131)
[3]     N               sequence; phone sends 0, ACKs echo the N of the packet they answer
[4]     cmd             low nibble: 1 SEND, 2 SEND_NO_ACK, 3 REQUEST, 4 ACK
[5]     dataType        see table in section 4
[6..7]  00 00           CRC16 slot, unused
[8..9]  len             payload length, uint16 little-endian
[10..19] payload[0..9]  first 10 payload bytes (zero padded)
```
**Follow-up page k (1..pages)**
```
[0]     k
[1..19] payload[10 + (k-1)*19 ...]   zero padded
```
With a bigger MTU the SDK simply concatenates several 20-byte pages into one write. Sending one
20-byte page per write (MTU 20 mode) works. ✅

**ACK** (`CEProtocolB.getSendData`, cmd `-10001` = `CMD_APP_ACK_TYPE`)
```
00 01 00 <N> 04 <dataType> 00 00 01 00 <status> 00...   status: 1 ok, 2 wrong, 3 crc wrong, 4 over
```
- The watch ACKs every SEND/REQUEST from the phone. ✅
- The phone must ACK every data packet from the watch, echoing its `dataType` and `N`
  (`proxy/CEDevQueue.java:171-180`). ✅ (the watch otherwise retries)

**Example, device info** ✅
```
-> 00 01 00 00 03 02 00 00 00 00 00 ...                      REQUEST devinfo
<- 00 a9 00 00 04 02 00 00 01 00 01 ...                      ACK ok
<- 00 a9 01 01 01 02 00 00 0c 00 0b a9 33 02 08 00 0f 12 03 85   head, 1 follow-up, len 12
<- 01 7c 08 01 00 be 12 1c 01 00 ...                         page 1
-> 00 01 00 01 04 02 00 00 01 00 01 ...                      our ACK (N=1)
payload: 0b a9 33 02 08 00 | 0f 12 03 85 7c 08  (items, customer, hw, code, picture, font | MAC reversed)
```

---

## 3. Payloads

All integers little-endian. Strings are raw UTF-8 (no emoji filtering anywhere in the app).

### Device info: REQUEST type 2 ✅
Send `cmd 3, type 2`, no payload (`K6SendDataManager.getDevInfo()`).
Reply type 2 (`entity/k6/K6_DevInfoStruct.parseDevInfo`): `items, customer_id, hardware_id, code_id,
picture_id, font_id [, customer_id_h if items == 12]`. Version string = `customer.hw.code.picture.font`.

### Find watch: SEND type 11 ✅
`K6_DATA_TYPE_FIND_PHONE_OR_DEVICE`: one byte `onoff`. The app only ever sends `01`
(`com/boAt/wristgear/view/ui/watch/o1.java:740`). The watch ACKs, then rings/vibrates.
The **same type 11 coming from the watch** means "find my phone" (`ProcessDATA_TYPE_FIND_PHONE`).

### Set time: SEND type 104 ✅
`entity/k6/K6_CESyncTime`, 9 bytes:
```
u32 unix seconds | i32 timezone offset seconds | flags (bit0 = time format, bit1 = month/day order)
```
Sent by the app on every connect (also inside the type 110 mix packet). The exact meaning of
flag bit0 (12h vs 24h) is not confirmed; `01` was accepted.

### Notification: SEND type 107 ✅ (emoji bytes accepted; rendering depends on the watch font)
`entity/k6/K6_MessageNoticeStruct`:
```
u32 unix seconds | type | count(=2) | 01 len name_utf8 | 02 len content_utf8
```
Limits from `addProperty()`: name ≤ 60-2-6 = 52 bytes; content ≤ 150 - (nameLen+2) - 8 bytes. The app
trims with `substring` and appends "...". `sendMessage_notice()` always uses attr 1 = name, attr 2 = content
(attr 0 = phone number exists but is unused).

Types (icon): 1 phone, 2 SMS, 3 QQ, 4 WeChat, 5 email, 6 Facebook, 7 Twitter, 8 WhatsApp, 9 Skype,
10 LinkedIn, 11 Line, 16 other, 17 Kakao, 18 Instagram, 19 Telegram.

Example ✅ (`"Claude 🤖"` / `"Hello from your laptop 👋🔥😎 it works! ✅"`, 70 bytes, 4 follow-ups):
```
-> 00 01 04 00 01 6b 00 00 46 00 ad 76 ef 6a 02 02 01 0b 43 6c
-> 01 61 75 64 65 20 f0 9f a4 96 02 31 48 65 6c 6c 6f 20 66 72
-> 02 6f 6d 20 79 6f 75 72 20 6c 61 70 74 6f 70 20 f0 9f 91 8b
-> 03 f0 9f 94 a5 f0 9f 98 8e 20 69 74 20 77 6f 72 6b 73 21 20
-> 04 e2 9c 85 00 ...
<- 00 a9 00 00 04 6b 00 00 01 00 01 ...   ACK ok
```

### Battery: type 3 (watch → phone) 📖
`ProcessDATA_TYPE_BATTERY_INFO`: `payload[0]` = percent. The app never requests it; the watch pushes it
(also inside the type 9 DEV_SYNC mix packet).

### Mix packets: type 110 (APP_SYNC, phone → watch) / type 9 (DEV_SYNC, watch → phone) 📖
`entity/k6/K6_MixInfoStruct`:
```
u16 total_len-2 | u8 count | { u16 item_len (incl. these 3 bytes) | u8 dataType | data } * count
```
The watch's type 9 reply is split up and each item is handled as if it arrived with its own dataType
(`ProcessDATA_TYPE_DEV_SYNC`). The app's `sendAsynInfoDetail()` builds the 110 packet from:
userinfo (102), time (104), message display (124 `01 ff ff 00 00`), call alarm (122), message alarm (123),
goal (111) and **pair finish (120)**. Because it includes 120 (pairing state) the web app does **not**
send it yet.

### History records 📖
- Sport, types 4 (real) / 5 (history), `ProcessDATA_TYPE_SPORT` + `K6_Sport`:
  `u16 ? | u8 count | count × { u32 start_unix | u32 steps | u24 distance | u24 kcal | u24 duration }`
  (each record 20 bytes; the u24 fields sit in 4-byte slots).
- Heart, types 7 (real) / 8 (history), `K6_HeartStruct`: records of `u32 time | u8 bpm` (5 bytes).
- Sleep, type 6, `ProcessDATA_TYPE_SLEEP` + `K6_Sleep`: `.. | u8 count(@2) | count × { u8 n | 15 × (u8 type | u32 time) }`,
  first `n` entries valid. type: 1 start, 2 deep, 3 light, 4 wake.
- Live HR switch, SEND type 24, `K6_DATA_TYPE_REAL_HR`: `01` on / `00` off.

---

## 4. All data types (`CEBC.K6`)

| Type | Name | Notes |
|---|---|---|
| 2 | DEVINFO | ✅ request |
| 3 | BATTERY_INFO | watch → phone |
| 4 / 5 | REAL_SPORT / HISTORY_SPORT | watch → phone |
| 6 | SLEEP | watch → phone |
| 7 / 8 | REAL_HEART / HISTORY_HEART | watch → phone |
| 9 | DEV_SYNC | mix packet from watch |
| 10 | MIX_SPORT | |
| 11 | FIND_PHONE | ✅ both directions |
| 12 | BLE_PAIR_STATUS | |
| 13 | USER_CHANGE | |
| 14 | MUSIC_CONTROL | watch → phone |
| 15 / 117 | CALL_CONTROL to app / to dev | |
| 16 | GSENSOR_TEST_DATA | factory |
| 17 | EXERCISE_HEART | |
| 18 / 19 / 20 / 24 | REAL_BP / REAL_ECG / REAL_O2 / REAL_HR | live measurement switches |
| 21 | HR_CONTROL | |
| 22 | FUNCTION_CONTROL | |
| 23 | HARDWARE_INFO | |
| 25 | BTEDR_ADDR | request (classic BT address) |
| 26 / 27 / 28 | QR_CODE info / del / clear | |
| 29 | PHONE_RESOLUTION | |
| 30 | SMS_REPLY | |
| 60 | NOUSE | |
| 61 | SPORT_ITEM_SET | |
| 62 | SET_HEART_MAX | |
| 63 / 64 | EXERCISE_CMD / EXERCISE_STATUS | |
| 66 | SWIM_SETTING | |
| 67 | GPS_ARGUMENT | |
| 68 / 71 | TEST_GPS_CMD / TEST_GPS_DATA | ⛔ factory |
| 69 | APP_BOND | ⛔ |
| 70 | PAIR_START | ⛔ |
| 72 | SETTING | |
| 73 | HISTORY_GPS | |
| 102 | USERINFO | |
| 103 | LANGUAGE_SETTING | |
| 104 | TIME | ✅ |
| 105 | WEATHER | |
| 106 | ALARM | |
| 107 | MESSAGE_NOTICE | ✅ |
| 108 | APP_CLOSE | |
| 109 | SET_DATA_SWITCH | |
| 110 | APP_SYNC | mix packet from phone (contains 120) |
| 111 | SET_TARGET | goals |
| 112 | OPEN_BLE_PAIR | ⛔ |
| 113 | MUSIC_CONTENT | |
| 114 | SITTING_REMIND | |
| 115 | FORGET_DISTURB | do-not-disturb |
| 116 | PHOTOGRAPH_ONOFF | camera |
| **118** | **RESET** | ⛔ `sendDeviceRestart()` |
| **119** | **SHUTDOWN** | ⛔ |
| 120 | PAIR_FINISH | ⛔ |
| 121 | UNIT_SETTING | |
| 122 / 123 / 124 | CALL_ALARM / MESSAGE_ALARM / MESSAGE_DISPLAY | |
| 125 | TARGET_ALARM | |
| 126 | DRINK_ALARM | |
| 127 | HAND_RISE_SWITCH | |
| 128 | HEART_AUTO_SWITCH | |
| 129 | WATCH_SETTING | |
| 130 | APP_SPORT | |
| **131** | **WATCHFACE_SYNC** | ⛔ bulk file push, special paging (>255 pages, `FE`/`FF` markers) |
| 132 | WATCHFACE_INFO | request |
| 133 | WOMAN_STAGE_INFO | |
| 134 | WATCHFACE_START | |
| 135 / 136 / 137 / 138 | CONTACT add / delete / clean / sync | ⛔ 137 wipes contacts |
| 139 | REAL_TIME_WEATHER | |
| 140 / 141 | WATCHFACE_PHOTO_DEL / POWER_LOGO_DEL | ⛔ deletes |
| **201 / 202** | **OTA_STATUS / OTA_DATA** | ⛔ firmware |
| 203 | TEST_DEBUG | ⛔ |

---

## 5. Never send

`118` reset, `119` shutdown, `201`/`202` OTA, `131` watch-face/file push, `69`/`70`/`112`/`120`
pairing/bond, `137` contact wipe, `27`/`28`/`140`/`141` deletes, `16`/`68`/`71`/`203` factory/test.
Both `cli/flash.py` and `web/index.html` use a hard **allowlist** (only types 2, 11, 104, 107 + ACKs),
so none of these can go out by accident.
