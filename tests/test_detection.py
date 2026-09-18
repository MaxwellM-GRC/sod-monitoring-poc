from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import yaml

from src.detection import evaluate
from src.loaders import load_sources


ROOT = Path(__file__).resolve().parents[1]


def sample():
    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    return config, load_sources(config, ROOT)


def test_sample_finds_individual_unmitigated_conflicts():
    config, sources = sample()
    findings, conflicts, matrix, coverage = evaluate(config, *sources)

    assert len(conflicts) == 6
    assert len(findings) == 6
    assert {row.rule for row in findings} == {"SOD-02", "SOD-04"}
    assert sum(row.severity == "critical" for row in findings) == 3
    assert sum(row.severity == "high" for row in findings) == 3
    assert all(row["result"] == "pass" for row in matrix)
    assert all(row["result"] == "pass" for row in coverage)


def test_valid_compensating_controls_are_retained_as_evidence_not_findings():
    config, sources = sample()
    findings, conflicts, _, _ = evaluate(config, *sources)

    accepted = {row["user_id"]: row for row in conflicts if row["result"] == "accepted_with_effective_control"}
    assert set(accepted) == {"u200", "u700"}
    assert accepted["u200"]["latest_control_test"]["evidence_ref"] == "GRC-CC-200-2026-W36"
    assert not any(row.user_id in accepted for row in findings)


def test_inactive_accounts_are_preserved_but_not_evaluated_as_active_conflicts():
    config, sources = sample()
    findings, conflicts, _, _ = evaluate(config, *sources)

    assert not any(row["user_id"] == "u600" for row in conflicts)
    assert not any(row.user_id == "u600" for row in findings)


def test_failed_control_and_expired_exception_cause_sod04_findings():
    config, sources = sample()
    findings, _, _, _ = evaluate(config, *sources)
    governance = {row.user_id: row.detail for row in findings if row.rule == "SOD-04"}

    assert "expired on 2026-08-31" in governance["u300"]
    assert "latest compensating control test result is failed" in governance["u400"]


def test_unapproved_matrix_rule_causes_sod01_finding():
    config, sources = sample()
    accounts, entitlements, matrix, risks, exceptions, tests = sources
    matrix[0] = replace(matrix[0], status="draft")

    findings, _, matrix_results, _ = evaluate(config, accounts, entitlements, matrix, risks, exceptions, tests)
    assert any(row.rule == "SOD-01" and row.object_id == "SOD-R001" for row in findings)
    assert next(row for row in matrix_results if row["conflict_rule_id"] == "SOD-R001")["result"] == "exception"


def test_missing_cross_application_rule_causes_sod03_finding():
    config, sources = sample()
    accounts, entitlements, matrix, risks, exceptions, tests = sources
    matrix = [row for row in matrix if row.conflict_rule_id != "SOD-R001"]

    findings, _, _, coverage = evaluate(config, accounts, entitlements, matrix, risks, exceptions, tests)
    assert any(row.rule == "SOD-03" and row.object_id == "BP-AP-01" for row in findings)
    assert next(row for row in coverage if row["process_risk_id"] == "BP-AP-01")["result"] == "exception"


def test_generic_accounts_are_in_scope():
    config, sources = sample()
    findings, conflicts, _, _ = evaluate(config, *sources)
    assert any(row["user_id"] == "gen800" and row["account_types"] == ["generic"] for row in conflicts)
    assert any(row.user_id == "gen800" and row.rule == "SOD-02" for row in findings)
