# Segregation of Duties Monitoring — Proof of Concept

**This cloud native ITGC proof of concept correlates account, entitlement, governance, and compensating control evidence across four applications to detect incompatible access.**

![CI](https://github.com/MaxwellM-GRC/sod-monitoring-poc/actions/workflows/ci.yml/badge.svg)

> **Sanitized demonstration.** All names, people, organizations, systems, accounts, and records in this repository are fictional. No employer, client, or production data is included.

## The problem it catches

Financial access rarely lives in one system. A user might maintain vendor master data in an ERP and release payments in a treasury platform, so reviewing either application alone can miss the conflict. A user might also prepare and approve the same journal entry or submit and approve the same expense.

The fictional full population covers Coranto ERP, Atlas Treasury, Nimbus Expense, and Quill Billing. It includes human, privileged, generic, service, and disabled accounts. The sample deliberately produces six findings:

- three critical conflicts between vendor maintenance and payment release, including one generic account;
- one high expense submitter and approver conflict with an expired exception;
- one high exception governance finding for that expired exception; and
- one high exception governance finding where the compensating control failed.

Two other conflicts are accepted because their approvals are current and their compensating controls have recent, independent, passing evidence. Disabled access remains in the source population but is excluded from results for active conflicts.

## What this control tests

| Control ID | Control description | Severity |
|---|---|---|
| SOD-01 | The applied rule set matches the current approved SoD matrix. | High |
| SOD-02 | No active user holds an unmitigated incompatible access combination. | Critical |
| SOD-03 | Cross application conflicts are included where the business process spans systems. | High |
| SOD-04 | Accepted conflicts have a current owner, approval, compensating control, and periodic reassessment. | High |

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

Each source is checked against `data/source_manifest.json` for evidence source details, expected fields, row count, evidence integrity, extraction timestamp, query description, and review window. Missing, changed, duplicated, or unreconciled source records stop the review with exit code `3` rather than producing a misleading clean result.

The evaluator then reconciles every entitlement to an application account and common identity, confirms that the matrix is approved and current, verifies that business process risks have matrix coverage, and evaluates the full active population. A retained conflict is accepted only when its owner, approval, expiry, reassessment date, compensating control, evidence, and independent review are current.

Automation detects, prioritizes, and routes an exception case. Authorized people approve remediation, risk acceptance, and closure. They also decide whether to remove access, redesign a role, approve time bound mitigation, complete the lookback, and accept the documented root cause. The tool cannot change access, accept risk, attest that a control operated, or approve its own follow up.

## Quick start

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# Run the sample review and write output/
.venv/bin/python -m src.main

# Run tests
.venv/bin/python -m pytest -q
```

The normal run exits `0` after a valid evaluation, even when it finds conflicts. `--fail-on-findings` returns `2` after writing evidence so monitoring can alert. Invalid source or population evidence returns `3`.

## Sample output

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

The generated evidence package contains:

```text
output/
  control_evidence.json   Evidence source details, complete population check, evaluations, findings
  exceptions.csv          Exception register ready for review with blank human decision fields
  cases/SOD-*.md          One response case per individual finding
```

A demonstration of that package is checked into [`sample_output/`](sample_output/), including one markdown case for every seeded finding.

## Continuous monitoring

- `ci.yml` runs the test suite and a sample review for every change.
- `sod-monitor.yml` runs each weekday and on demand, retains the evidence package, and opens or updates one GitHub Issue per finding.
- `exception-escalation.yml` runs daily and labels overdue open cases `sla-breached`, with an escalation comment to the control owner.
- Each exception case has a five day response SLA. Critical conflicts that can create and approve or release a financial transaction require immediate escalation to Financial Systems Controls.
- When a finding disappears from a later run, the workflow adds `human-closure-review`. It does not close the Issue automatically because remediation, lookback, root cause, and closure evidence still require human review.

The scheduled monitor uses `--fail-on-findings` after it has preserved evidence and synchronized Issues. A red run is therefore the expected alert for the seeded sample rather than a processing failure.

## Production design and limitations

This repository uses sanitized static CSV files. A production implementation would use collectors with read only, least privilege access to the identity, ERP, treasury, expense, billing, and GRC services. Collector output would be stored immutably before normalization and reconciled to each authoritative system inventory.

Production readiness also requires validated identity correlation, explicit treatment of service and generic accounts, approved matrix change governance, encrypted evidence storage, dedicated system identities with limited access, monitored collection failures, retention controls, and user acceptance testing for every rule. See [Production design](docs/production_design.md) for the deployment boundary and readiness gates.

The proof of concept demonstrates detection and evidence packaging. It does not establish that a production population is complete, make access changes, approve exceptions, perform transaction lookbacks, or approve case closure. Those activities remain human decisions owned by authorized control and business process personnel.

## Control mapping

| RCM attribute | Definition |
|---|---|
| Control ID | `ITGC-SOD-001` |
| Control name | Segregation of Duties Monitoring |
| Risk category | `logical_access` |
| Risk | Failure to identify and resolve incompatible access combinations could allow a user to initiate and conceal an error or fraud without independent review, resulting in unauthorized or inaccurate financial transactions. |
| Control description | Management performs periodic analysis of complete active user entitlement populations against the approved segregation of duties matrix and remediates or formally mitigates identified conflicts. |
| Objective | Incompatible duties within and across in scope systems are identified, prevented, remediated, or mitigated through approved compensating controls. |
| Population | All active human, privileged, generic, and applicable service accounts with roles and permissions across in scope systems. |
| Frequency | Weekly detective monitoring; formal management review at least quarterly. |
| Framework alignment | SOX ITGC logical access and segregation of duties; NIST SP 800-53 AC-5; COBIT 2019 DSS05.04. |
| Evidence contract | Evidence source details, complete population check, matrix and coverage evaluations, individual findings, exception cases, response evidence, and human approved closure. |

Detailed mapping and evidence requirements are in [RCM and control narrative](docs/rcm_and_control_narrative.md) and [Evidence contract](docs/evidence_contract.md). Response ownership is defined in the [Human response runbook](docs/human_response_runbook.md).

## Repository layout

```text
config.yaml                 Control, sources, matrix rules, and response guidance
data/*/accounts.csv         Complete fictional application account populations
data/*/entitlements.csv     Complete fictional entitlement populations
data/governance/            Approved matrix, process risks, exceptions, control tests
data/source_manifest.json   Evidence source details, counts, and integrity checks
src/                        Integrity checks, detection, models, and reporting
tests/                      Rule, fail closed, reconciliation, and output tests
docs/                       Narrative, evidence contract, response, production design
.github/workflows/           CI, scheduled monitoring, and SLA escalation
sample_output/              Evidence ready for review and individual cases
```

## Shared terminology

Plain language definitions for shared assurance terms are available in the
[portfolio glossary](https://github.com/MaxwellM-GRC/grc-control-core/blob/v0.1.1/docs/glossary.md).

MIT — see [LICENSE](LICENSE).
