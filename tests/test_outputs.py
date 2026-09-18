from __future__ import annotations

import csv
import json
from pathlib import Path

from src.main import ROOT, run
from src.reporting import write_cases, write_evidence, write_exceptions


def test_evidence_and_rcm_outputs_reconcile(tmp_path: Path):
    result, config = run(ROOT / "config.yaml", ROOT / "data/source_manifest.json")
    evidence_path = tmp_path / "control_evidence.json"
    exceptions_path = tmp_path / "exceptions.csv"
    cases_path = tmp_path / "cases"
    write_evidence(result, config, evidence_path)
    write_exceptions(result, config, exceptions_path)
    write_cases(result, config, cases_path)

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    with exceptions_path.open(newline="", encoding="utf-8") as handle:
        exceptions = list(csv.DictReader(handle))

    assert evidence["input_valid"] is True
    assert evidence["population_reconciled"] is True
    assert evidence["population"]["active_accounts"] == 14
    assert evidence["population"]["active_account_entitlements"] == 16
    assert len(exceptions) == len(evidence["findings"]) == 6
    assert len(list(cases_path.glob("SOD-*.md"))) == 6
    assert all(row["management_decision"] == "" for row in exceptions)


def test_run_id_and_finding_ids_are_reperformable():
    first, _ = run(ROOT / "config.yaml", ROOT / "data/source_manifest.json")
    second, _ = run(ROOT / "config.yaml", ROOT / "data/source_manifest.json")
    assert first.run_id == second.run_id
    assert [row.finding_id for row in first.findings] == [row.finding_id for row in second.findings]
