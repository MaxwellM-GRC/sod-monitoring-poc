from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_readme_uses_portfolio_sections_and_exact_control_table():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    headings = [
        "## The problem it catches",
        "## What this control tests",
        "## How it works",
        "## Quick start",
        "## Sample output",
        "## Continuous monitoring",
        "## Production design and limitations",
        "## Control mapping",
        "## Repository layout",
    ]
    assert [text.index(value) for value in headings] == sorted(text.index(value) for value in headings)
    assert "| Control ID | Control description | Severity |" in text
    for rule, definition in config["rules"].items():
        expected = f"| {rule} | {definition['assertion']} | {definition['severity'].title()} |"
        assert expected in text


def test_required_control_metadata_and_narratives_are_present():
    config = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    control = config["control"]
    for field in ("id", "source_checklist", "risk_category", "risk", "control_description", "objective", "activity", "frequency", "owner"):
        assert control[field]
    assert control["risk"].startswith("Failure to ") and " could " in control["risk"]
    assert control["control_description"].startswith("Management performs ")
    for path in ("evidence_contract.md", "rcm_and_control_narrative.md", "production_design.md"):
        assert (ROOT / "docs" / path).is_file()


def test_human_decision_boundary_and_escalation_are_explicit():
    decision = "Authorized people approve remediation, risk acceptance, and closure."
    assert decision in (ROOT / "README.md").read_text(encoding="utf-8")
    assert decision in (ROOT / "docs" / "production_design.md").read_text(encoding="utf-8")
    assert decision in (ROOT / "docs" / "rcm_and_control_narrative.md").read_text(encoding="utf-8")
    assert (ROOT / ".github" / "workflows" / "exception-escalation.yml").is_file()
