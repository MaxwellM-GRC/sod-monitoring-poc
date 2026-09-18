"""Write reproducible evidence, an RCM ready finding log, and one case per finding."""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from .models import ReviewResult


EXCEPTION_COLUMNS = [
    "run_id", "finding_id", "control_id", "rule", "assertion", "severity",
    "object_type", "object_id", "conflict_rule_id", "user_id", "display_name",
    "account_type", "applications", "account_ids", "entitlements", "risk_statement",
    "detail", "exception_id", "remediation", "mitigation", "root_cause",
    "closure_evidence", "escalation", "status", "response_owner",
    "management_decision", "closure_approved_by", "closure_date",
]


def build_payload(result: ReviewResult, config: dict) -> dict:
    counts = Counter(finding.severity for finding in result.findings)
    conflict_counts = Counter(row["result"] for row in result.conflict_evaluations)
    return {
        "schema_version": "1.0",
        "run_id": result.run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "control": config["control"],
        "review": config["review"],
        "rules": config["rules"],
        "response_governance": config["response_governance"],
        "input_valid": result.input_valid,
        "population_reconciled": result.population_reconciled,
        "population": {
            "accounts_all_statuses": result.account_count,
            "active_accounts": result.active_account_count,
            "entitlements_all_statuses": result.entitlement_count,
            "active_account_entitlements": result.active_entitlement_count,
            "active_identities": result.active_identity_count,
            "approved_effective_matrix_rules": result.matrix_rule_count,
            "cross_application_matrix_rules": result.cross_application_rule_count,
            "conflicts_detected": len(result.conflict_evaluations),
            "conflict_results": dict(sorted(conflict_counts.items())),
        },
        "source_provenance": [status.as_dict() for status in result.source_status],
        "population_errors": result.population_errors,
        "matrix_evaluations": result.matrix_evaluations,
        "coverage_evaluations": result.coverage_evaluations,
        "conflict_evaluations": result.conflict_evaluations,
        "counts_by_severity": dict(sorted(counts.items())),
        "findings": [finding.as_dict() for finding in result.findings],
    }


def write_evidence(result: ReviewResult, config: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_payload(result, config), indent=2) + "\n", encoding="utf-8")


def write_exceptions(result: ReviewResult, config: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=EXCEPTION_COLUMNS,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        writer.writeheader()
        for finding in result.findings:
            writer.writerow({
                "run_id": result.run_id,
                **finding.as_dict(),
                "status": "Open - human decision required",
                "response_owner": config["response_governance"]["escalation_owner"],
                "management_decision": "",
                "closure_approved_by": "",
                "closure_date": "",
            })


def write_cases(result: ReviewResult, config: dict, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for finding in result.findings:
        content = f"""# SoD exception {finding.finding_id}

- **Run ID:** `{result.run_id}`
- **Control / rule:** `{finding.control_id}` / `{finding.rule}`
- **Severity:** {finding.severity}
- **Conflict rule:** `{finding.conflict_rule_id or 'not applicable'}`
- **User / object:** `{finding.user_id or finding.object_id}` — {finding.display_name or finding.object_type}
- **Accounts:** {finding.account_ids or 'not applicable'}
- **Applications:** {finding.applications or 'not applicable'}
- **Entitlements:** {finding.entitlements or 'not applicable'}
- **Existing exception:** `{finding.exception_id or 'none'}`
- **Status:** Open — human decision required

## Control assertion

{finding.assertion}

## Risk and detection detail

{finding.risk_statement or config['control']['risk']}

{finding.detail}

## Human approved response

- [ ] Accountable owner assigned.
- [ ] Management chose and approved access removal, role redesign, or a time bound compensating control: {finding.remediation}
- [ ] Exposure period analysis completed: {finding.mitigation}
- [ ] Root cause documented: {finding.root_cause}
- [ ] Closure package attached: {finding.closure_evidence}
- [ ] Escalation requirement assessed: {finding.escalation}
- [ ] Closure approved by `{config['control']['owner']}` or an authorized delegate.

## Decision record

| Field | Human entry |
|---|---|
| Response owner | |
| Decision and rationale | |
| Approved by / date | |
| Remediation completed at | |
| Lookback conclusion | |
| Closure evidence links | |
| Closure approved by / date | |

Automation may detect, route, and recommend. It must not remove access, accept
risk, attest that a compensating control operated, or close this case.
"""
        (directory / f"{finding.finding_id}.md").write_text(content, encoding="utf-8")


def print_summary(result: ReviewResult) -> None:
    counts = Counter(finding.severity for finding in result.findings)
    print("SEGREGATION OF DUTIES MONITORING CONTROL")
    print(f"Run ID: {result.run_id}")
    print(f"Input provenance valid: {result.input_valid}")
    print(f"Population reconciled: {result.population_reconciled}")
    print(f"Active accounts / identities: {result.active_account_count} / {result.active_identity_count}")
    print(f"Active entitlements evaluated: {result.active_entitlement_count}")
    print(f"Effective matrix rules / cross application: {result.matrix_rule_count} / {result.cross_application_rule_count}")
    print(f"Conflicts detected: {len(result.conflict_evaluations)}")
    print(f"Findings: {len(result.findings)} ({dict(sorted(counts.items()))})")
    for finding in result.findings:
        print(f"[{finding.severity.upper()}] {finding.rule} {finding.object_id}: {finding.detail}")
