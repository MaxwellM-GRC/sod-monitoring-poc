# ITGC-SOD-001 RCM and control narrative

## Risk

Failure to identify and resolve incompatible access combinations could allow a user to initiate and conceal an error or fraud without independent review, resulting in unauthorized or inaccurate financial transactions.

## Control description

Management performs periodic analysis of complete active user entitlement populations against the approved segregation of duties matrix and remediates or formally mitigates identified conflicts.

| RCM attribute | Definition |
|---|---|
| Control ID | `ITGC-SOD-001` |
| Control name | Segregation of Duties Monitoring |
| Risk category | `logical_access` |
| Objective | Incompatible duties within and across in scope systems are identified, prevented, remediated, or mitigated through approved compensating controls. |
| Frequency | Weekly detective monitoring; formal management review at least quarterly. |
| Control owner | Financial Systems Controls |
| Nature | Automated detection with response and closure owned by authorized people. |

## Activity

1. Collect authoritative account and entitlement populations from every in scope application for the same review cutoff.
2. Validate source identity, collection method, query, period, schema, row count, uniqueness, and SHA-256 fingerprint.
3. Reconcile every entitlement to an application account and common user identifier. Stop the run if the population cannot be reconciled.
4. Confirm that the deployed rules are approved, effective, and match the authorized SoD matrix version.
5. Reconcile the business process risk inventory to the matrix so risks across applications cannot silently fall outside monitoring.
6. Evaluate each active identity against all applicable rule pairs within and across applications.
7. Assess each conflict against approved exception ownership, approval, expiry, reassessment, and compensating control evidence.
8. Route unsupported findings into individual exception cases with stable identifiers and retain the human response record.

## Population

The control population is all active human, privileged, generic, and applicable service accounts with roles and permissions across Coranto ERP, Atlas Treasury, Nimbus Expense, and Quill Billing. Disabled accounts remain in retained source extracts but are excluded from active conflict evaluation. The run separately reconciles entitlement rows to accounts and the business process risk inventory to the approved matrix.

## Evidence

The RCM ready evidence package contains:

- retained fictional input extracts and `data/source_manifest.json` with source provenance, row counts, review windows, and SHA-256 fingerprints;
- a deterministic run ID derived from the configuration and source fingerprints;
- source integrity and population reconciliation results;
- matrix approval, effective date, version, and business process coverage evaluations;
- every detected conflict, including effectively mitigated conflicts;
- individual findings and exception cases with owner, remediation, lookback, root cause, closure evidence, SLA, escalation, and recurrence guidance; and
- human approval and closure fields that automation intentionally leaves blank.

See [Evidence contract](evidence_contract.md) for the artifact schema and retention expectations.

## Human decision boundary

Automation detects, prioritizes, and routes. Authorized people approve remediation, risk acceptance, and closure. They also determine lookback scope, assess compensating control performance, document root cause, and decide whether access removal, role redesign, or a time bound exception is appropriate.

Automation must not change access, approve an exception, accept risk, attest control performance, or close a case. A finding that disappears from a later run is labeled for human closure review and remains open until the required evidence and approval are recorded.

## Framework alignment

| Framework | Illustrative alignment |
|---|---|
| SOX ITGC | Logical access and segregation of duties over systems that support financial reporting. |
| NIST SP 800-53 Rev. 5 | `AC-5`, Separation of Duties. |
| COBIT 2019 | `DSS05.04`, Manage user identity and logical access. |

Framework alignment supports control design and cross reference. It does not replace management's scoping, risk assessment, or control ownership decisions.

