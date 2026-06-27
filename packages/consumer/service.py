#!/usr/bin/env python3
# Part of the ifURI solution — pakiet KONSUMENTA (proces 2).
"""Serwis HTTP udostępniający ``file/command/restore``. Przyjmuje ``snapshot`` po transporcie,
WALIDUJE wejście wobec inp-schematu wspólnego kontraktu (odrzuca śmieci od kogokolwiek), odtwarza
plik z bajtów snapshotu, waliduje własne wyjście. Ładuje TEN SAM contracts.json co producent.

  POST /run  {snapshot}  →  koperta file/command/restore
  GET  /health           →  {"ok": true}
"""
from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "toolkit"))
from contract_gate import check  # noqa: E402
from contracts_io import load  # noqa: E402

ROUTE = "file/command/restore"
CONTRACTS, _ = load()
C = CONTRACTS[ROUTE]


def restore_handler(snapshot: dict) -> dict:
    return {"ok": True, "connector": "filepair", "action": "file-restore",
            "did": f"restore({snapshot.get('path', '?')})", "reversible": True,
            "inverse": {"path": "file/command/snapshot-delete", "args": {"path": snapshot.get("path")}}}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _err(self, code, msg, extra: dict | None = None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        body = {"ok": False, "error": msg}
        if extra:
            body.update(extra)
        self.wfile.write(json.dumps(body).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
        payload = json.loads(body or b"{}")
        try:
            check(C.inp, payload, "inp")
        except AssertionError as exc:
            return self._err(422, f"input violates {ROUTE}: {exc}")
        snap = payload.get("snapshot") or {}
        if not isinstance(snap, dict):
            return self._err(422, f"input violates {ROUTE}: snapshot must be obj")
        if not snap.get("path"):
            return self._err(422, "snapshot.path required",
                             {"remediation": {"class": "snapshot-path-missing"}})
        env = restore_handler(snap)
        try:
            check(C.out, env, "out")
        except AssertionError as exc:
            return self._err(500, f"output violates {ROUTE}: {exc}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(env).encode())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8802"))
    print(f"consumer: {ROUTE} na :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
