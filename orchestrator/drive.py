#!/usr/bin/env python3
# Part of the ifURI solution — ORCHESTRATOR / brama międzyprocesowa po transporcie.
"""Steruje wymianą między dwoma WDROŻONYMI procesami po HTTP, wiążąc je wspólnym kontraktem:

  1. POST producent  →  koperta file/command/snapshot-delete
  2. zastosuj krawędź WIRES (snapshot-delete→restore: snapshot→snapshot) → wejście konsumenta
  3. consumer_input_check → potwierdź PEŁNY handoff (snapshot to całe wejście restore)
  4. POST konsument z tym wejściem  →  koperta file/command/restore
  5. zwaliduj odpowiedź; exit 0/1

Procesy nie współdzielą obiektu Pythona — tylko JSON na sieci i TEN SAM contracts.json."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "toolkit"))
from contract_gate import check, consumer_input_check, find_wire, wire_payload  # noqa: E402
from contracts_io import load  # noqa: E402

PRODUCER = os.environ.get("PRODUCER_URL", "http://localhost:8801")
CONSUMER = os.environ.get("CONSUMER_URL", "http://localhost:8802")
PROD_ROUTE = "file/command/snapshot-delete"
CONS_ROUTE = "file/command/restore"
CONTRACTS, WIRES = load()


def post(url: str, payload: dict) -> dict:
    req = urllib.request.Request(url + "/run", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def wait_ready(url, tries=40):
    for _ in range(tries):
        try:
            urllib.request.urlopen(url + "/health", timeout=1); return True
        except Exception:
            time.sleep(0.5)
    raise SystemExit(f"serwis {url} nie wstał")


def main() -> int:
    wait_ready(PRODUCER); wait_ready(CONSUMER)
    prod_env = post(PRODUCER, {"path": "/tmp/a.txt"})
    check(CONTRACTS[PROD_ROUTE].out, prod_env, "producer.out")

    wire = find_wire(WIRES, PROD_ROUTE, CONS_ROUTE)
    payload = wire_payload(wire, prod_env)
    mode, problems = consumer_input_check(CONTRACTS[CONS_ROUTE], payload, wire)
    if problems:
        print(f"  ✗ krawędź niezgodna ({mode}): {problems}")
        return 1

    cons_env = post(CONSUMER, payload)
    check(CONTRACTS[CONS_ROUTE].out, cons_env, "consumer.out")

    print(f"  [OK ] producer ──HTTP──▶ consumer   ({mode} handoff)")
    print(f"        snapshot.path = {prod_env['snapshot']['path']}")
    print(f"        restore did   = {cons_env['did']}")
    print("  dwa wdrożone pakiety różnych URI, jeden kontrakt, wymiana po transporcie: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
