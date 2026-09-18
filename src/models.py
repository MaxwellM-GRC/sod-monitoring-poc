"""Normalized source records and RCM ready review structures."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from hashlib import sha256


@dataclass(frozen=True)
class Account:
    application: str
    account_id: str
    user_id: str
    display_name: str
    account_type: str
    status: str
    is_privileged: bool
    as_of: str


@dataclass(frozen=True)
class Entitlement:
    application: str
    account_id: str
    user_id: str
    entitlement: str
    assigned_at: str


@dataclass(frozen=True)
class MatrixRule:
    conflict_rule_id: str
    business_process: str
    risk_statement: str
    left_application: str
    left_entitlement: str
    right_application: str
    right_entitlement: str
    severity: str
    cross_application: bool
    matrix_version: str
    status: str
    approved_by: str
    approved_at: str
    effective_from: str
    effective_to: str


@dataclass(frozen=True)
class ApprovedException:
    exception_id: str
    conflict_rule_id: str
    user_id: str
    status: str
    owner: str
    approved_by: str
    approved_at: str
    expires_at: str
    compensating_control_id: str
    reassessment_due_at: str
    rationale: str


@dataclass(frozen=True)
class ControlTest:
    test_id: str
    exception_id: str
    compensating_control_id: str
    period_end: str
    tested_at: str
    performer: str
    reviewer: str
    result: str
    evidence_ref: str


@dataclass
class SourceStatus:
    source_id: str
    kind: str
    application: str
    path: str
    source_uri: str = ""
    extraction_method: str = ""
    query: str = ""
    extracted_at: str = ""
    window_start: str = ""
    window_end: str = ""
    expected_rows: int = 0
    actual_rows: int = 0
    expected_sha256: str = ""
    actual_sha256: str = ""
    missing_columns: list[str] = field(default_factory=list)
    duplicate_keys: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing_columns and not self.duplicate_keys and not self.errors

    def as_dict(self) -> dict:
        payload = asdict(self)
        payload["ok"] = self.ok
        return payload


@dataclass(frozen=True)
class Finding:
    control_id: str
    rule: str
    assertion: str
    severity: str
    object_type: str
    object_id: str
    conflict_rule_id: str
    user_id: str
    display_name: str
    account_type: str
    applications: str
    account_ids: str
    entitlements: str
    risk_statement: str
    detail: str
    exception_id: str
    remediation: str
    mitigation: str
    root_cause: str
    closure_evidence: str
    escalation: str

    @property
    def finding_id(self) -> str:
        seed = "|".join(
            [self.control_id, self.rule, self.object_type, self.object_id]
        )
        return f"SOD-{sha256(seed.encode()).hexdigest()[:16]}"

    def as_dict(self) -> dict:
        return {"finding_id": self.finding_id, **asdict(self)}


@dataclass
class ReviewResult:
    run_id: str
    findings: list[Finding]
    conflict_evaluations: list[dict]
    matrix_evaluations: list[dict]
    coverage_evaluations: list[dict]
    source_status: list[SourceStatus]
    population_errors: list[str]
    account_count: int = 0
    active_account_count: int = 0
    entitlement_count: int = 0
    active_entitlement_count: int = 0
    active_identity_count: int = 0
    matrix_rule_count: int = 0
    cross_application_rule_count: int = 0

    @property
    def input_valid(self) -> bool:
        return all(source.ok for source in self.source_status) and not self.population_errors

    @property
    def population_reconciled(self) -> bool:
        return self.input_valid and self.active_account_count > 0 and self.active_entitlement_count > 0
