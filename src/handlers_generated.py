# WYGENEROWANE Z contracts.json — NIE EDYTUJ RĘCZNIE.
# Przegeneruj: `make gen`. Bramą jest ci/regen_check.py.
from typing import Any

# from .conn import conn, _ok  # zapewnione przez pakiet connectora

@conn.handler("file/command/restore", isolated=True, meta={"label": "TODO: file/command/restore"})
def restore(snapshot: dict | None = None) -> dict[str, Any]:
    """WYGENEROWANE Z KONTRAKTU v1. Sygnatura i kształt koperty pochodzą z
    contracts.json — NIE edytuj ich ręcznie (build odrzuci dryf). Uzupełnij tylko ciało."""
    raise NotImplementedError("ciało file/command/restore")  # noqa: F841 — uzupełnij logikę, potem:
    return _ok(action='file-restore', reversible=True, inverse={"path": 'file/command/snapshot-delete', "args": {"path": ""}})

@conn.handler("file/command/snapshot-delete", isolated=True, meta={"label": "TODO: file/command/snapshot-delete"})
def snapshot_delete(path: str = "") -> dict[str, Any]:
    """WYGENEROWANE Z KONTRAKTU v1. Sygnatura i kształt koperty pochodzą z
    contracts.json — NIE edytuj ich ręcznie (build odrzuci dryf). Uzupełnij tylko ciało."""
    raise NotImplementedError("ciało file/command/snapshot-delete")  # noqa: F841 — uzupełnij logikę, potem:
    return _ok(action='file-snapshot-delete', reversible=True, snapshot={}, inverse={"path": 'file/command/restore', "args": {"snapshot": {}}})
