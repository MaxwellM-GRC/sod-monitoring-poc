"""Command line runner for the ITGC-SOD-001 proof of concept."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

from .detection import evaluate
from .integrity import validate_population, validate_sources
from .loaders import load_sources
from .models import ReviewResult
from .reporting import print_summary, write_cases, write_evidence, write_exceptions


ROOT = Path(__file__).resolve().parents[1]


def _run_id(config_path: Path, statuses) -> str:
    payload = {
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "sources": [(status.source_id, status.actual_sha256) for status in statuses],
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return f"RUN-{digest[:16]}"


def run(config_path: Path, manifest_path: Path) -> tuple[ReviewResult, dict]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    statuses = validate_sources(config, ROOT, manifest_path)
    run_id = _run_id(config_path, statuses)
    empty = ReviewResult(run_id, [], [], [], [], statuses, [])
    if not all(status.ok for status in statuses):
        return empty, config

    accounts, entitlements, matrix, risks, exceptions, tests = load_sources(config, ROOT)
    population_errors = validate_population(accounts, entitlements)
    if population_errors:
        empty.population_errors = population_errors
        return empty, config

    findings, conflicts, matrix_eval, coverage_eval = evaluate(
        config, accounts, entitlements, matrix, risks, exceptions, tests
    )
    active_keys = {(row.application, row.account_id) for row in accounts if row.status == "active"}
    active_entitlements = [row for row in entitlements if (row.application, row.account_id) in active_keys]
    as_of = config["review"]["as_of"]
    version = config["review"]["approved_matrix_version"]
    current_matrix = [row for row in matrix if row.status == "approved" and row.matrix_version == version and row.effective_from <= as_of <= row.effective_to]
    result = ReviewResult(
        run_id=run_id, findings=findings, conflict_evaluations=conflicts,
        matrix_evaluations=matrix_eval, coverage_evaluations=coverage_eval,
        source_status=statuses, population_errors=population_errors,
        account_count=len(accounts), active_account_count=len(active_keys),
        entitlement_count=len(entitlements), active_entitlement_count=len(active_entitlements),
        active_identity_count=len({row.user_id for row in accounts if row.status == "active"}),
        matrix_rule_count=len(current_matrix),
        cross_application_rule_count=sum(row.cross_application for row in current_matrix),
    )
    return result, config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config.yaml")
    parser.add_argument("--manifest", type=Path, default=ROOT / "data/source_manifest.json")
    parser.add_argument("--evidence-json", type=Path, default=ROOT / "output/control_evidence.json")
    parser.add_argument("--exceptions-csv", type=Path, default=ROOT / "output/exceptions.csv")
    parser.add_argument("--cases-dir", type=Path, default=ROOT / "output/cases")
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args(argv)

    result, config = run(args.config, args.manifest)
    write_evidence(result, config, args.evidence_json)
    write_exceptions(result, config, args.exceptions_csv)
    if result.input_valid:
        write_cases(result, config, args.cases_dir)
    print_summary(result)
    if not result.input_valid:
        for source in result.source_status:
            if not source.ok:
                print(f"INVALID SOURCE {source.source_id}: {source.errors}")
        for error in result.population_errors:
            print(f"INVALID POPULATION: {error}")
        return 3
    if args.fail_on_findings and result.findings:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
