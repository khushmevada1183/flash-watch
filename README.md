# flash-watch

Control my boAt **FLASH** smartwatch straight from a browser (or a Python script) instead of the
boAt Wearables app. It talks Bluetooth Low Energy, no pairing, no account, no cloud.

The protocol was worked out by decompiling the boAt Wearables APK (`com.boAt.wristgear` 3.5.4) and
then testing on the real watch. Full byte-level notes, every data type, and the source locations in
the decompiled app are in **[SYSTEM.md](SYSTEM.md)**.

## The watch

- Shows up as `FLASH`, MAC `08:7C:85:03:12:0F`
- Firmware `169.51.2.8.0` (customer 169, hardware 51)
- One custom BLE service `0xF618`: write to `0xB002`, notifications on `0xB001`
- Speaks the CE "K6" protocol from the `ce.com.cenewbluesdk` SDK bundled in the boAt app
- This is **not** the KaHa protocol used by the boAt PRISM ([udaysinh-git/boat-watch](https://github.com/udaysinh-git/boat-watch));
  same brand, different vendor, totally different bytes

## What works

| Feature | Type | Status |
|---|---|---|
| Device info / firmware version | REQUEST 2 | ✅ tested |
| Find watch (rings/vibrates) | SEND 11 | ✅ tested |
| Set time + timezone | SEND 104 | ✅ tested |
| Notifications with emoji, choose app icon | SEND 107 | ✅ tested (emoji bytes accepted; rendering depends on the watch font) |
| "Find my phone" from the watch → beep in browser | 11 from watch | 📖 from code |
| Battery % | 3 from watch | 📖 shown when the watch pushes it |
| Steps / heart / sleep history | 4-8 | 📖 decoded in SYSTEM.md, not wired into a sync yet |

## Web app

### Which browsers can reach the watch?

| Where you open the page | Web Bluetooth in the browser | Through `server.py` |
|---|---|---|
| Chrome / Edge / Opera, desktop or Android | ✅ (Linux: may need a flag) | ✅ |
| Brave (desktop / Android) | only with `brave://flags/#brave-web-bluetooth-api` | ✅ |
| Firefox (any) | ❌ never | ✅ |
| **Any iOS browser** (Safari, Brave, Chrome on iPhone are all WebKit) | ❌ never | ✅ |

So `server.py` is the way to cover every browser: the PC holds the Bluetooth link and browsers just
load a page from it.

### Option 1 (works in every browser): bridge on this PC

```sh
python3 server.py           # this PC only: http://localhost:8000
python3 server.py --lan     # phones/tablets on the same Wi-Fi: open the printed http://<ip>:8000/?t=<token>
```

`server.py` serves `web/` and drives the watch through the PC's own Bluetooth (BlueZ over D-Bus),
connecting it if needed. Stdlib + system `dbus`/`gi` only. Default bind is `127.0.0.1`; `--lan`
binds all interfaces and requires a random per-run token on every API call (the printed URL carries
it). API: `POST /api/{connect,info,find,time,notify}`, `GET /api/events?since=N`, `GET /api/status`.

Limit: the watch has to stay in Bluetooth range of the PC. To drop the PC entirely on iPhone you need a
native app (see Next ideas).

### Option 2: pure Web Bluetooth (phone / no server)

Deploy to Vercel or Netlify (configs included: `vercel.json`, `netlify.toml`, both publish `web/`),
then on your device open the HTTPS URL and tap **Connect Watch**. Don't pair the watch in the phone's
Bluetooth settings or keep the boAt app running: the site connects through the browser's own device
picker, and a watch that is already held by another app stops advertising.

**Browser Compatibility Guide:**
- **Android / Desktop Chrome, Edge, Samsung Internet, Opera:** Works out of the box on HTTPS.
- **iPhone / iPad:** Standard iOS Safari/Chrome uses WebKit which blocks Web Bluetooth. Open the site in the free **[Bluefy Web BLE Browser](https://apps.apple.com/app/bluefy-web-ble-browser/id1492822055)** (one-tap button included on iOS).
- **Brave Browser:** Enable `brave://flags/#brave-web-bluetooth-api`, set to *Enabled*, and relaunch.
- **Mozilla Firefox:** Firefox does not support Web Bluetooth; use Chrome, Edge, Bluefy, or Option 1 (`server.py`).
- **Progressive Web App (PWA):** Installable to your phone's home screen with offline caching via `sw.js`.

Packet self-check (compares against the bytes the real watch accepted):

```sh
node web/check.js
```

## CLI (Linux, BlueZ)

`cli/flash.py` uses the system `dbus` + `gi` Python modules, nothing to pip install. It connects the
watch if it isn't already (it must be paired with this PC once).

```sh
python3 cli/flash.py                         # device info
python3 cli/flash.py find                    # ring the watch
python3 cli/flash.py time                    # sync clock
python3 cli/flash.py notify "Hi 😀" "from my laptop 🎉"
WATCH_MAC=AA:BB:... python3 cli/flash.py     # another watch
```

## Protocol in 30 seconds

20-byte pages, no checksum.

```
head:     00 | devType(01) | pages | N | cmd | dataType | 00 00 | len(u16 LE) | 10 payload bytes
follow:   k  | 19 payload bytes
cmd:      1 send, 3 request, 4 ack
ack:      00 01 00 N 04 dataType 00 00 01 00 01   (watch acks everything; we ack every data packet it sends)
```

Notification payload: `u32 unix | icon | 02 | 01 len title | 02 len text` (UTF-8, title ≤ 52 B,
title+text ≤ ~150 B, each emoji is 4 B).

## Don't brick it

Both the web app and the CLI have a hard **allowlist**: only data types 2, 11, 104, 107 and ACKs can
be sent. That keeps these out of reach:

`118` reset · `119` shutdown · `201/202` firmware OTA · `131` watch-face/file push ·
`69/70/112/120` pairing/bond · `137` wipe contacts · `27/28/140/141` deletes · `16/68/71/203` factory/test

Add a new command only after reading its struct in the decompiled app (see SYSTEM.md section 4) and
adding it to `ALLOWED` in both files.

## Next ideas

- Phone-native app without a PC: wrap `web/index.html` with Capacitor + `@capacitor-community/bluetooth-le`
  (one codebase, Android + iOS; iOS needs Xcode to install). On iPhone, the Bluefy browser also
  implements Web Bluetooth.

- Weather (105 / 139), alarms (106), do-not-disturb (115), raise-to-wake (127), auto heart rate (128)
- Live heart rate (24) and a step/sleep sync. The app's sync packet (110) includes `PAIR_FINISH` (120),
  so that needs care before sending.
- Re-decompile yourself: `jadx --no-res -d out com.boAt.wristgear.apk`, then look in
  `sources/ce/com/cenewbluesdk/`.

The APK and the decompiled code are not included: they belong to boAt and the SDK vendor.
