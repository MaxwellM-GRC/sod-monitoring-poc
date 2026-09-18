"""Refresh fixture row counts and hashes after an intentional source update."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    sources = []
    for source in config["sources"]:
        path = ROOT / source["path"]
        with path.open(newline="", encoding="utf-8") as handle:
            row_count = sum(1 for _ in csv.DictReader(handle))
        sources.append({
            "source_id": source["id"],
            "source_uri": f"fictional://{source['application']}/{source['kind']}",
            "extraction_method": "Sanitized static export for portfolio demonstration",
            "query": f"SELECT required control fields FROM {source['kind']} FOR COMPLETE REVIEW WINDOW",
            "extracted_at": "2026-09-16T08:00:00Z",
            "window_start": config["review"]["window_start"],
            "window_end": config["review"]["window_end"],
            "row_count": row_count,
            "sha256": sha256(path),
        })
    payload = {"schema_version": "1.0", "sources": sources}
    (ROOT / "data/source_manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

