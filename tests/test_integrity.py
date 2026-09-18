from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from src.integrity import validate_population, validate_sources
from src.models import Account, Entitlement


def test_manifest_hash_mismatch_fails_closed(tmp_path: Path):
    source = tmp_path / "accounts.csv"
    source.write_text("account_id,user_id\nA-1,u1\n", encoding="utf-8")
    config = {
        "review": {"window_start": "2026-09-01T00:00:00Z", "window_end": "2026-09-15T23:59:59Z"},
        "sources": [{"id": "accounts", "kind": "accounts", "application": "app", "path": "accounts.csv", "key_fields": ["account_id"], "required_columns": ["account_id", "user_id"]}],
    }
    manifest = {
        "sources": [{
            "source_id": "accounts", "source_uri": "fictional://app/accounts",
            "extraction_method": "test", "query": "all accounts", "extracted_at": "2026-09-16T00:00:00Z",
            "window_start": config["review"]["window_start"], "window_end": config["review"]["window_end"],
            "row_count": 1, "sha256": "not-the-file-hash",
        }]
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    status = validate_sources(config, tmp_path, path)[0]
    assert not status.ok
    assert "manifest SHA-256 does not match source" in status.errors


def test_population_rejects_orphan_entitlement():
    accounts = [Account("app", "A-1", "u1", "User", "human", "active", False, "2026-09-15")]
    entitlements = [Entitlement("app", "A-2", "u1", "ROLE", "2026-01-01T00:00:00Z")]
    assert validate_population(accounts, entitlements) == ["orphan entitlement app/A-2/ROLE"]

