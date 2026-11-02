#!/usr/bin/env python3
"""HTTP bridge: UI ↔ system commands via file-based IPC."""
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler

CMD_DIR = "/var/lib/nexus/bridge/cmd"
RESP_DIR = "/var/lib/nexus/bridge/resp"
STATE = "/var/lib/nexus/bridge/state.json"

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n).decode()
        if self.path == "/cmd":
            cmd = json.loads(body)
            cid = cmd.get("id", "unknown")
            with open(f"{CMD_DIR}/{cid}.json", "w") as f:
                json.dump(cmd, f)
            self._send({"ok": True})
        else: self._send({"err": "404"}, 404)

    def do_GET(self):
        if self.path == "/state":
            try:
                with open(STATE) as f: self._send(json.load(f))
            except: self._send({"status": "idle"})
        elif self.path.startswith("/resp/"):
            cid = self.path[6:]
            try:
                with open(f"{RESP_DIR}/{cid}.json") as f: self._send(json.load(f))
            except: self._send({"err": "pending"}, 404)
        else: self._send({"err": "404"}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _send(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a): pass

if __name__ == "__main__":
    os.makedirs(CMD_DIR, exist_ok=True)
    os.makedirs(RESP_DIR, exist_ok=True)
    HTTPServer(("127.0.0.1", 9377), H).serve_forever()