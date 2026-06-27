#!/usr/bin/env python3
# Part of the ifURI solution — pakiet PRODUCENTA (proces 1).
"""Serwis HTTP udostępniający ``file/command/snapshot-delete`` po transporcie. Robi snapshot
pliku (path + bajty base64 + sha256), zwraca go jako ``snapshot`` i ``inverse`` wskazujący
``file/command/restore``. Waliduje kopertę wobec out-schematu wspólnego kontraktu PRZED wysłaniem.

  POST /run  {path?}  →  koperta file/command/snapshot-delete (snapshot + inverse)
  GET  /health        →  {"ok": true}
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
from contract_gate import check  # noqa: E402
from contracts_io import load  # noqa: E402

ROUTE = "file/command/snapshot-delete"
CONTRACTS, _ = load()
C = CONTRACTS[ROUTE]


def snapshot_delete_handler(path: str = "/tmp/a.txt") -> dict:
    # demo: snapshot a fixed payload (a real impl reads+removes the file before returning)
    data = b"hello world"
    snapshot = {"path": path, "content_b64": base64.b64encode(data).decode(),
                "sha256": hashlib.sha256(data).hexdigest()}
    return {"ok": True, "connector": "filepair", "action": "file-snapshot-delete",
            "did": f"snapshot-delete({path})", "reversible": True, "snapshot": snapshot,
            "inverse": {"path": "file/command/restore", "args": {"snapshot": snapshot}}}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
        payload = json.loads(body or b"{}")
        env = snapshot_delete_handler(path=payload.get("path", "/tmp/a.txt"))
        try:
            check(C.out, env, "out")
        except AssertionError as exc:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": f"output violates {ROUTE}: {exc}"}).encode())
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(env).encode())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8801"))
    print(f"producer: {ROUTE} na :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
