"""Local bridge: serves web/ and talks to the watch through this PC's Bluetooth (BlueZ).

    python3 server.py            this PC only: http://localhost:8000
    python3 server.py --lan      any phone/browser on your Wi-Fi (prints a URL with a token)

No browser Bluetooth support needed: Safari, iOS Brave/Chrome, Firefox, anything works,
because the PC holds the Bluetooth link. Stdlib + the system dbus/gi modules only.
LAN mode requires a random token on every API call.
"""
import json
import secrets
import socket
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from gi.repository import GLib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "cli"))
import flash  # noqa: E402

WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
PORT = int(os.environ.get("PORT", 8000))
LAN = "--lan" in sys.argv
TOKEN = secrets.token_urlsafe(12) if LAN else None

events, lock = [], threading.Lock()


def record(ev):
    with lock:
        events.append(ev)
        del events[:-500]           # ponytail: in-memory ring of 500, fine for one user
    print(ev, flush=True)


watch = flash.Watch(on_event=record)


def on_glib(fn):
    """Run fn on the GLib/D-Bus thread and wait for its result."""
    done, box = threading.Event(), {}

    def run():
        try:
            box["ok"] = fn()
        except Exception as e:      # report D-Bus/BlueZ errors to the page
            box["err"] = str(e)
        done.set()
        return False
    GLib.idle_add(run)
    done.wait(30)
    if "err" in box:
        raise RuntimeError(box["err"])
    return box.get("ok")


def ensure_connected():
    if not (watch.connected() and watch.tx):
        watch.connect()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=WEB, **kw)

    def reply(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def authed(self):
        if TOKEN and not secrets.compare_digest(self.headers.get("X-Token", ""), TOKEN):
            self.reply(403, {"error": "bad token: open the exact URL server.py printed"})
            return False
        return True

    def do_GET(self):
        if self.path.startswith("/api/") and not self.authed():
            return
        if self.path.startswith("/api/events"):
            since = int(self.path.partition("since=")[2] or 0)
            with lock:
                total = len(events)
                return self.reply(200, {"next": total, "events": events[since:] if since <= total else events})
        if self.path == "/api/status":
            return self.reply(200, {"bridge": True, "mac": flash.MAC, "connected": watch.connected()})
        return super().do_GET()

    def do_POST(self):
        if not self.authed():
            return
        name = self.path.removeprefix("/api/")
        try:
            if name == "connect":
                on_glib(ensure_connected)
                return self.reply(200, {"connected": True})
            if name not in flash.COMMANDS:
                return self.reply(404, {"error": "unknown command"})
            kw = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            on_glib(lambda: (ensure_connected(), watch.write(flash.COMMANDS[name](**kw))))
            return self.reply(200, {"sent": name})
        except Exception as e:
            return self.reply(500, {"error": str(e)})

    def log_message(self, *_):
        pass


def main():
    srv = ThreadingHTTPServer(("0.0.0.0" if LAN else "127.0.0.1", PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    if LAN:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))   # no packet sent; just picks the LAN interface
            ip = s.getsockname()[0]
        print(f"open on any device on this Wi-Fi: http://{ip}:{PORT}/?t={TOKEN}", flush=True)
    else:
        print(f"open http://localhost:{PORT}  (watch {flash.MAC})", flush=True)
    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
