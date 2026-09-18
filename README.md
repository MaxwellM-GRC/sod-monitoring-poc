# Segregation of Duties Monitoring — Proof of Concept

![CI](https://github.com/MaxwellM-GRC/sod-monitoring-poc/actions/workflows/ci.yml/badge.svg)

**A cloud native ITGC proof of concept that detects incompatible access within and across applications, validates approved mitigations, and produces an RCM ready evidence package.**

Financial access rarely lives in one system. A user might maintain vendor master data in an ERP and release payments in a treasury platform, so reviewing either application alone can miss the conflict. This repository evaluates complete entitlement populations for active accounts across four fictional applications against a versioned, approved SoD matrix.

> **Sanitized demonstration.** Every person, system, identifier, transaction reference, approval, and evidence location in this repository is fictional. No employer, client, or production data is included.

## What the sample demonstrates

The fictional population covers Coranto ERP, Atlas Treasury, Nimbus Expense, and Quill Billing. It includes human, privileged, generic, service, and disabled accounts. The approved matrix defines conflicts within and across applications for procure to pay, record to report, travel and expense, treasury, and order to cash.

The sample deliberately produces six findings:

- three critical unmitigated conflicts between vendor maintenance and payment release, including one generic account;
- one high expense submitter/approver conflict with an expired exception;
- one high exception governance finding for that expired exception; and
- one high exception governance finding where the compensating control failed.

Two other conflicts are accepted because their approvals are current and their compensating controls have recent, independent, passing evidence. Disabled access is retained in the source population but excluded from results for active conflicts.

## Control design

| Rule | Assertion | Default severity |
|---|---|---|
| SOD-01 | The applied rule set matches the current approved SoD matrix. | High |
| SOD-02 | No active user holds an unmitigated incompatible access combination. | Critical, or the matrix rule severity |
| SOD-03 | Cross application conflicts are included where the business process spans systems. | High |
| SOD-04 | Accepted conflicts have a current owner, approval, compensating control, and periodic reassessment. | High |

The control uses the portfolio standard language for `ITGC-SOD-001`:

> Management performs periodic analysis of complete active user entitlement populations against the approved segregation of duties matrix and remediates or formally mitigates identified conflicts.

Automation detects and routes exceptions. A human must decide whether to remove access, redesign a role, or approve a time bound compensating control. The tool cannot remove access, accept risk, attest that a control operated, or close its own cases.

## How it works

```text
Application account exports ─┐
Application entitlements ────┼─► validate provenance ─► reconcile population
Approved SoD matrix ─────────┤                                  │
Business process risk map ───┤                                  ▼
Approved exceptions ─────────┼─► match incompatible access ─► assess mitigation
Compensating control tests ──┘                                  │
                                                               ▼
                                             evidence JSON + RCM CSV + cases
```

Each source is checked against `data/source_manifest.json` for its expected schema, row count, SHA-256 fingerprint, extraction timestamp, query description, and review window. Missing, changed, duplicated, or unreconciled source records stop the review with exit code `3` rather than producing a misleading clean result.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# Run the sample review and write output/
.venv/bin/python -m src.main

# Run tests
.venv/bin/python -m pytest -q
```

Expected summary:

```text
SEGREGATION OF DUTIES MONITORING CONTROL
Input provenance valid: True
Population reconciled: True
Active accounts / identities: 14 / 9
Active entitlements evaluated: 16
Effective matrix rules / cross application: 5 / 2
Conflicts detected: 6
Findings: 6 ({'critical': 3, 'high': 3})
```

Generated evidence:

```text
output/
  control_evidence.json   Provenance, population reconciliation, all evaluations, findings
  exceptions.csv          RCM ready exception register with blank human decision fields
  cases/SOD-*.md          One response case per individual finding
```

A demonstration of that package is checked into [`sample_output/`](sample_output/), including one markdown case for every seeded finding.

The normal run exits `0` after a valid evaluation, even when it finds conflicts. `--fail-on-findings` returns `2` after writing evidence so monitoring can alert. Invalid source or population evidence returns `3`.

## Continuous monitoring

- `ci.yml` runs the test suite and a sample review for every change.
- `sod-monitor.yml` runs each weekday and on demand, retains the evidence package, opens or updates one GitHub Issue per finding, labels disappeared findings for human closure review, and then turns red when actionable findings remain.

The monitor never closes an Issue automatically. A conflict disappearing from the next extract is evidence for a reviewer, not proof that remediation and lookback are complete.

## Repository map

```text
config.yaml                 Control, sources, matrix rules, and response guidance
data/*/accounts.csv         Complete fictional application account populations
data/*/entitlements.csv     Complete fictional entitlement populations
data/governance/            Approved matrix, process risks, exceptions, control tests
data/source_manifest.json   Source provenance, counts, and fingerprints
src/                        Integrity checks, detection, models, and reporting
tests/                      Rule, fail closed, reconciliation, and output tests
docs/                       Narrative, evidence contract, response, production design
sample_output/              RCM ready evidence and individual cases
```

See [Control narrative](docs/control_narrative.md), [Evidence contract](docs/evidence_contract.md), [Human response runbook](docs/human_response_runbook.md), and [Production design](docs/production_design.md).

MIT — see [LICENSE](LICENSE).
