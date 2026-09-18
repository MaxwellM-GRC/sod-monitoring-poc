"""Evaluate all four ITGC-SOD-001 assertions across the complete population."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import date, timedelta

from .models import Account, ApprovedException, ControlTest, Entitlement, Finding, MatrixRule


def _date(value: str) -> date:
    return date.fromisoformat(value)


def _pair(left_app: str, left_ent: str, right_app: str, right_ent: str) -> tuple[tuple[str, str], tuple[str, str]]:
    return tuple(sorted(((left_app, left_ent), (right_app, right_ent))))  # type: ignore[return-value]


def _finding(config: dict, rule_id: str, object_type: str, object_id: str, *,
             conflict_rule_id: str = "", user_id: str = "", display_name: str = "",
             account_type: str = "", applications: str = "", account_ids: str = "",
             entitlements: str = "", risk_statement: str = "", detail: str,
             exception_id: str = "", severity: str | None = None) -> Finding:
    response = config["rule_responses"][rule_id]
    return Finding(
        control_id=config["control"]["id"], rule=rule_id,
        assertion=config["rules"][rule_id]["assertion"],
        severity=severity or config["rules"][rule_id]["severity"],
        object_type=object_type, object_id=object_id,
        conflict_rule_id=conflict_rule_id, user_id=user_id, display_name=display_name,
        account_type=account_type, applications=applications, account_ids=account_ids,
        entitlements=entitlements, risk_statement=risk_statement, detail=detail,
        exception_id=exception_id, remediation=response["remediation"],
        mitigation=response["mitigation"], root_cause=response["root_cause"],
        closure_evidence=response["closure_evidence"], escalation=response["escalation"],
    )


def _matrix_ok(rule: MatrixRule, version: str, as_of: date) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    if rule.matrix_version != version:
        reasons.append(f"version {rule.matrix_version} is not approved version {version}")
    if rule.status != "approved" or not rule.approved_by or not rule.approved_at:
        reasons.append("approval evidence is incomplete")
    if not (_date(rule.effective_from) <= as_of <= _date(rule.effective_to)):
        reasons.append("rule is outside its effective period")
    return not reasons, reasons


def _exception_assessment(exc: ApprovedException | None, tests: list[ControlTest], as_of: date,
                          max_age_days: int) -> tuple[bool, list[str], ControlTest | None]:
    if exc is None:
        return False, ["no approved exception"], None
    reasons: list[str] = []
    if exc.status != "approved":
        reasons.append("exception status is not approved")
    for field in ("owner", "approved_by", "approved_at", "compensating_control_id", "reassessment_due_at"):
        if not getattr(exc, field):
            reasons.append(f"{field} is blank")
    if _date(exc.expires_at) < as_of:
        reasons.append(f"exception expired on {exc.expires_at}")
    if _date(exc.reassessment_due_at) < as_of:
        reasons.append(f"reassessment was due on {exc.reassessment_due_at}")
    matching = [row for row in tests if row.exception_id == exc.exception_id and row.compensating_control_id == exc.compensating_control_id and _date(row.tested_at) <= as_of]
    latest = max(matching, key=lambda row: row.tested_at, default=None)
    if latest is None:
            reasons.append("no compensating control test was found")
    else:
        if latest.result != "pass":
            reasons.append(f"latest compensating control test result is {latest.result}")
        if not latest.evidence_ref:
            reasons.append("latest compensating control test lacks evidence")
        if latest.performer == latest.reviewer:
            reasons.append("compensating control test lacks independent review")
        if _date(latest.tested_at) < as_of - timedelta(days=max_age_days):
            reasons.append("latest compensating control test is stale")
    return not reasons, reasons, latest


def evaluate(config: dict, accounts: list[Account], entitlements: list[Entitlement],
             matrix: list[MatrixRule], process_risks: list[dict], exceptions: list[ApprovedException],
             tests: list[ControlTest]) -> tuple[list[Finding], list[dict], list[dict], list[dict]]:
    findings: list[Finding] = []
    conflicts: list[dict] = []
    matrix_evaluations: list[dict] = []
    coverage_evaluations: list[dict] = []
    as_of = _date(config["review"]["as_of"])
    version = config["review"]["approved_matrix_version"]
    current_rules: list[MatrixRule] = []

    for rule in matrix:
        ok, reasons = _matrix_ok(rule, version, as_of)
        matrix_evaluations.append({"conflict_rule_id": rule.conflict_rule_id, "matrix_version": rule.matrix_version, "approved": rule.status == "approved", "effective": not reasons or "rule is outside its effective period" not in reasons, "result": "pass" if ok else "exception", "reasons": reasons})
        if ok:
            current_rules.append(rule)
        else:
            findings.append(_finding(config, "SOD-01", "matrix_rule", rule.conflict_rule_id, conflict_rule_id=rule.conflict_rule_id, risk_statement=rule.risk_statement, detail="; ".join(reasons)))

    covered_pairs = {_pair(r.left_application, r.left_entitlement, r.right_application, r.right_entitlement): r for r in current_rules}
    for risk in process_risks:
        key = _pair(risk["left_application"], risk["left_entitlement"], risk["right_application"], risk["right_entitlement"])
        covered = key in covered_pairs
        coverage_evaluations.append({"process_risk_id": risk["process_risk_id"], "business_process": risk["business_process"], "cross_application": risk["cross_application"].lower() == "true", "covered_by_conflict_rule": covered_pairs[key].conflict_rule_id if covered else "", "result": "pass" if covered else "exception"})
        if not covered:
            findings.append(_finding(config, "SOD-03", "business_process_risk", risk["process_risk_id"], applications=f"{risk['left_application']} | {risk['right_application']}", entitlements=f"{risk['left_entitlement']} | {risk['right_entitlement']}", detail=f"Approved matrix does not cover {risk['business_process']} risk {risk['process_risk_id']}."))

    active_accounts = [row for row in accounts if row.status == "active"]
    accounts_by_user: dict[str, list[Account]] = defaultdict(list)
    access_by_user: dict[str, set[tuple[str, str]]] = defaultdict(set)
    entitlement_accounts: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    active_account_keys = {(row.application, row.account_id) for row in active_accounts}
    for account in active_accounts:
        accounts_by_user[account.user_id].append(account)
    for item in entitlements:
        if (item.application, item.account_id) in active_account_keys:
            access_by_user[item.user_id].add((item.application, item.entitlement))
            entitlement_accounts[(item.user_id, item.application, item.entitlement)].add(item.account_id)

    exceptions_by_key = {(row.user_id, row.conflict_rule_id): row for row in exceptions}
    for rule in current_rules:
        left = (rule.left_application, rule.left_entitlement)
        right = (rule.right_application, rule.right_entitlement)
        for user_id, access in sorted(access_by_user.items()):
            if left not in access or right not in access:
                continue
            user_accounts = accounts_by_user[user_id]
            display_name = sorted({row.display_name for row in user_accounts})[0]
            account_types = sorted({row.account_type for row in user_accounts})
            account_ids = sorted(entitlement_accounts[(user_id, *left)] | entitlement_accounts[(user_id, *right)])
            exception = exceptions_by_key.get((user_id, rule.conflict_rule_id))
            mitigation_ok, reasons, latest_test = _exception_assessment(
                exception, tests, as_of, config["review"]["compensating_control_test_max_age_days"]
            )
            conflict_id = f"{user_id}:{rule.conflict_rule_id}"
            evaluation = {
                "conflict_id": conflict_id,
                "conflict_rule_id": rule.conflict_rule_id,
                "business_process": rule.business_process,
                "risk_statement": rule.risk_statement,
                "user_id": user_id,
                "display_name": display_name,
                "account_types": account_types,
                "applications": sorted({rule.left_application, rule.right_application}),
                "account_ids": account_ids,
                "entitlements": [f"{rule.left_application}:{rule.left_entitlement}", f"{rule.right_application}:{rule.right_entitlement}"],
                "cross_application": rule.cross_application,
                "exception": asdict(exception) if exception else None,
                "latest_control_test": asdict(latest_test) if latest_test else None,
                "mitigation_assessment": "effective" if mitigation_ok else "ineffective_or_absent",
                "mitigation_reasons": reasons,
                "result": "accepted_with_effective_control" if mitigation_ok else "unmitigated_conflict",
            }
            conflicts.append(evaluation)
            common = dict(
                conflict_rule_id=rule.conflict_rule_id, user_id=user_id, display_name=display_name,
                account_type=" | ".join(account_types), applications=" | ".join(evaluation["applications"]),
                account_ids=" | ".join(account_ids), entitlements=" | ".join(evaluation["entitlements"]),
                risk_statement=rule.risk_statement, exception_id=exception.exception_id if exception else "",
            )
            if not mitigation_ok:
                findings.append(_finding(config, "SOD-02", "user_conflict", conflict_id, severity=rule.severity, detail=f"Active incompatible access is not effectively mitigated: {'; '.join(reasons)}.", **common))
            if exception and not mitigation_ok:
                findings.append(_finding(config, "SOD-04", "accepted_exception", exception.exception_id, detail=f"Accepted conflict governance is not current or effective: {'; '.join(reasons)}.", **common))

    return findings, conflicts, matrix_evaluations, coverage_evaluations
