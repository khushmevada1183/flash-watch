"""Talk to the FLASH watch (boAt Wearables / CE "K6" protocol) over BlueZ D-Bus.

    python3 cli/flash.py                 device info (default)
    python3 cli/flash.py find            ring the watch
    python3 cli/flash.py time            sync the clock
    python3 cli/flash.py notify "T" "M"  push a notification (emoji ok)
    append a number to listen N seconds (default 8)

Uses the Bluetooth stack already on this PC (BlueZ); connects the watch if needed.
ACKs whatever the watch pushes back, like the app does. Also imported by ../server.py.
Protocol: ../SYSTEM.md
"""
import os
import sys
import time

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

MAC = os.environ.get("WATCH_MAC", "08:7C:85:03:12:0F")
DEV = "/org/bluez/hci0/dev_" + MAC.replace(":", "_")
TX_UUID = "0000b002-0000-1000-8000-00805f9b34fb"
RX_UUID = "0000b001-0000-1000-8000-00805f9b34fb"
CHR = "org.bluez.GattCharacteristic1"
PROPS = "org.freedesktop.DBus.Properties"

# Hard allowlist (cmd, dataType). Reset(118), shutdown(119), OTA(201/202), watch-face/file
# push(131), pairing/bond, deletes etc. can never go out. 4 = ACK, any type.
ALLOWED = {(3, 2), (1, 11), (1, 104), (1, 107)}


def pages(cmd, dtype, data=b"", n=0, ack_status=None):
    """20-byte pages: head [0,devType 1,pages,N,cmd,type,0,0,len LE,10 data] + [k, 19 data]."""
    if cmd != 4 and (cmd, dtype) not in ALLOWED:
        raise ValueError(f"blocked cmd={cmd} type={dtype}")
    head = bytearray(20)
    head[1], head[3], head[4], head[5] = 1, n, cmd, dtype
    if ack_status is not None:          # ACK: len 1, status at [10]
        head[8], head[10] = 1, ack_status
        return [bytes(head)]
    rest = data[10:]
    count = -(-len(rest) // 19)
    if count > 255:
        raise ValueError("payload too long")
    head[2] = count
    head[8:10] = len(data).to_bytes(2, "little")
    head[10:10 + min(10, len(data))] = data[:10]
    out = [bytes(head)]
    for i in range(count):
        chunk = rest[i * 19:(i + 1) * 19]
        out.append(bytes([i + 1]) + chunk + bytes(19 - len(chunk)))
    return out


def cut(text, limit):
    """Trim to <= limit UTF-8 bytes without splitting a character (emoji-safe)."""
    if len(text.encode()) <= limit:
        return text.encode()
    while len((text + "...").encode()) > limit:
        text = text[:-1]
    return (text + "...").encode()


def notice(title, body, kind=2):
    """K6_MessageNoticeStruct: u32 time | type | 2 | 01 len name | 02 len content."""
    name = cut(title, 52)
    content = cut(body, 150 - (len(name) + 2) - 8)
    return (int(time.time()).to_bytes(4, "little") + bytes([kind, 2])
            + bytes([1, len(name)]) + name + bytes([2, len(content)]) + content)


def timesync():
    """K6_CESyncTime: u32 unix | i32 tz offset s | flags (bit0 time format)."""
    off = -time.altzone if time.localtime().tm_isdst else -time.timezone
    return int(time.time()).to_bytes(4, "little") + off.to_bytes(4, "little", signed=True) + b"\x01"


COMMANDS = {
    "info": lambda **_: pages(3, 2),
    "find": lambda **_: pages(1, 11, b"\x01"),
    "time": lambda **_: pages(1, 104, timesync()),
    "notify": lambda title="", body="", kind=2, **_: pages(1, 107, notice(title, body, int(kind))),
}


def decode(dtype, data):
    if dtype == 2 and len(data) >= 6:
        return {"firmware": ".".join(str(x) for x in data[1:6])}
    if dtype == 3 and data:
        return {"battery": data[0]}
    if dtype == 11 and data:
        return {"find_phone": bool(data[0])}
    return {}


class Watch:
    """Holds the BlueZ connection; on_event(dict) gets every send/receive."""

    def __init__(self, on_event=print):
        self.on_event = on_event
        self.buf = None
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        self.bus = dbus.SystemBus()
        self.tx = self.rx = None

    def connect(self):
        dev = self.bus.get_object("org.bluez", DEV)
        if not dev.Get("org.bluez.Device1", "Connected", dbus_interface=PROPS):
            dbus.Interface(dev, "org.bluez.Device1").Connect()
        for _ in range(50):             # wait for GATT discovery
            if dev.Get("org.bluez.Device1", "ServicesResolved", dbus_interface=PROPS):
                break
            time.sleep(0.2)
        objs = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                              "org.freedesktop.DBus.ObjectManager").GetManagedObjects()
        for path, ifaces in objs.items():
            if path.startswith(DEV + "/") and CHR in ifaces:
                uuid = str(ifaces[CHR]["UUID"]).lower()
                if uuid == TX_UUID:
                    self.tx = dbus.Interface(self.bus.get_object("org.bluez", path), CHR)
                elif uuid == RX_UUID:
                    self.rx = dbus.Interface(self.bus.get_object("org.bluez", path), CHR)
                    self.bus.add_signal_receiver(self._on_props, "PropertiesChanged", PROPS, path=path)
        if not (self.tx and self.rx):
            raise RuntimeError("watch service 0xF618 not found")
        self.rx.StartNotify()

    def connected(self):
        try:
            dev = self.bus.get_object("org.bluez", DEV)
            return bool(dev.Get("org.bluez.Device1", "Connected", dbus_interface=PROPS))
        except dbus.DBusException:
            return False

    def write(self, pkts):
        for p in pkts:
            self.on_event({"dir": "->", "hex": p.hex(" ")})
            self.tx.WriteValue(dbus.Array(p, signature="y"), {"type": "request"})

    def _on_props(self, _iface, changed, _inv):
        if "Value" not in changed:
            return
        v = bytes(changed["Value"])
        self.on_event({"dir": "<-", "hex": v.hex(" ")})
        if v[0] != 0:                   # follow-up page
            if self.buf:
                self.buf["data"] += v[1:]
                if len(self.buf["data"]) >= self.buf["len"]:
                    self._done()
            return
        cmd, dtype = v[4] & 0x0F, v[5]
        if cmd == 4:
            self.on_event({"ack": dtype, "ok": v[10] == 1})
            return
        self.buf = {"cmd": cmd, "type": dtype, "n": v[3],
                    "len": int.from_bytes(v[8:10], "little"), "data": bytearray(v[10:])}
        if v[2] == 0 or len(self.buf["data"]) >= self.buf["len"]:
            self._done()

    def _done(self):
        b, self.buf = self.buf, None
        data = bytes(b["data"][:b["len"]])
        self.write(pages(4, b["type"], n=b["n"], ack_status=1))   # app ACKs every data packet
        self.on_event({"type": b["type"], "data": data.hex(" "), **decode(b["type"], data)})


def main():
    args = sys.argv[1:]
    w = Watch()
    w.connect()
    name = next((a for a in args if a in COMMANDS), "info")
    kw = {}
    if name == "notify":
        i = args.index("notify")
        kw = {"title": args[i + 1], "body": args[i + 2]}
    loop = GLib.MainLoop()
    GLib.timeout_add(500, lambda: (w.write(COMMANDS[name](**kw)), False)[1])
    GLib.timeout_add_seconds(next((int(a) for a in args if a.isdigit()), 8), loop.quit)
    loop.run()
    w.rx.StopNotify()


if __name__ == "__main__":
    main()
