"""Load normalized records from fictional source extracts."""

from __future__ import annotations

import csv
from pathlib import Path

from .models import Account, ApprovedException, ControlTest, Entitlement, MatrixRule


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _bool(value: str) -> bool:
    return value.strip().lower() == "true"


def load_sources(config: dict, root: Path) -> tuple[list[Account], list[Entitlement], list[MatrixRule], list[dict], list[ApprovedException], list[ControlTest]]:
    accounts: list[Account] = []
    entitlements: list[Entitlement] = []
    matrix: list[MatrixRule] = []
    process_risks: list[dict] = []
    exceptions: list[ApprovedException] = []
    tests: list[ControlTest] = []
    for source in config["sources"]:
        rows = _rows(root / source["path"])
        kind = source["kind"]
        app = source["application"]
        if kind == "accounts":
            accounts.extend(Account(app, row["account_id"], row["user_id"], row["display_name"], row["account_type"], row["status"], _bool(row["is_privileged"]), row["as_of"]) for row in rows)
        elif kind == "entitlements":
            entitlements.extend(Entitlement(app, row["account_id"], row["user_id"], row["entitlement"], row["assigned_at"]) for row in rows)
        elif kind == "sod_matrix":
            matrix.extend(MatrixRule(
                row["conflict_rule_id"], row["business_process"], row["risk_statement"],
                row["left_application"], row["left_entitlement"], row["right_application"],
                row["right_entitlement"], row["severity"], _bool(row["cross_application"]),
                row["matrix_version"], row["status"], row["approved_by"], row["approved_at"],
                row["effective_from"], row["effective_to"],
            ) for row in rows)
        elif kind == "business_process_risks":
            process_risks.extend(rows)
        elif kind == "exceptions":
            exceptions.extend(ApprovedException(**row) for row in rows)
        elif kind == "control_tests":
            tests.extend(ControlTest(**row) for row in rows)
    return accounts, entitlements, matrix, process_risks, exceptions, tests

