"""Fail closed source provenance, schema, and population integrity checks."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .models import Account, Entitlement, SourceStatus


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sources(config: dict, root: Path, manifest_path: Path) -> list[SourceStatus]:
    configured = {source["id"]: source for source in config["sources"]}
    if not manifest_path.exists():
        return [SourceStatus("manifest", "manifest", "governance", str(manifest_path), errors=["manifest missing"])]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [SourceStatus("manifest", "manifest", "governance", str(manifest_path), errors=[f"manifest unreadable: {exc}"])]

    entries = {entry.get("source_id", ""): entry for entry in manifest.get("sources", [])}
    statuses: list[SourceStatus] = []
    for source_id, source in configured.items():
        meta = entries.get(source_id, {})
        status = SourceStatus(
            source_id=source_id,
            kind=source["kind"],
            application=source["application"],
            path=source["path"],
            source_uri=meta.get("source_uri", ""),
            extraction_method=meta.get("extraction_method", ""),
            query=meta.get("query", ""),
            extracted_at=meta.get("extracted_at", ""),
            window_start=meta.get("window_start", ""),
            window_end=meta.get("window_end", ""),
            expected_rows=int(meta.get("row_count", 0)),
            expected_sha256=meta.get("sha256", ""),
        )
        path = root / source["path"]
        if not meta:
            status.errors.append("source absent from manifest")
        if not path.exists():
            status.errors.append("source file missing")
            statuses.append(status)
            continue
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
            headers = set(reader.fieldnames or [])
        status.actual_rows = len(rows)
        status.actual_sha256 = file_sha256(path)
        status.missing_columns = sorted(set(source["required_columns"]) - headers)
        keys = ["|".join(row.get(field, "").strip() for field in source["key_fields"]) for row in rows]
        status.duplicate_keys = sorted({key for key in keys if key and keys.count(key) > 1})
        if any(not key or "||" in f"|{key}|" for key in keys):
            status.errors.append("blank primary key component")
        if status.expected_rows != status.actual_rows:
            status.errors.append("manifest row count does not match source")
        if not status.expected_sha256 or status.expected_sha256 != status.actual_sha256:
            status.errors.append("manifest SHA-256 does not match source")
        for field in ("source_uri", "extraction_method", "query", "extracted_at", "window_start", "window_end"):
            if not getattr(status, field):
                status.errors.append(f"manifest {field} is blank")
        review = config["review"]
        if status.window_start != review["window_start"] or status.window_end != review["window_end"]:
            status.errors.append("manifest window does not equal configured review window")
        statuses.append(status)

    unexpected = set(entries) - set(configured)
    if unexpected and statuses:
        statuses[0].errors.append(f"unexpected manifest sources: {sorted(unexpected)}")
    return statuses


def validate_population(accounts: list[Account], entitlements: list[Entitlement]) -> list[str]:
    errors: list[str] = []
    account_index = {(row.application, row.account_id): row for row in accounts}
    for item in entitlements:
        account = account_index.get((item.application, item.account_id))
        if not account:
            errors.append(f"orphan entitlement {item.application}/{item.account_id}/{item.entitlement}")
        elif account.user_id != item.user_id:
            errors.append(f"identity mismatch for {item.application}/{item.account_id}/{item.entitlement}")
    for account in accounts:
        if account.status == "active" and not account.user_id.strip():
            errors.append(f"active account lacks identity correlation: {account.application}/{account.account_id}")
    return sorted(set(errors))
