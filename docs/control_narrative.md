# ITGC-SOD-001 control narrative and RCM mapping

## RCM ready definition

| Attribute | Definition |
|---|---|
| Control ID | ITGC-SOD-001 |
| Control name | Segregation of Duties Monitoring |
| Risk category | Logical access |
| Risk | Failure to identify and resolve incompatible access combinations could allow a user to initiate and conceal an error or fraud without independent review, resulting in unauthorized or inaccurate financial transactions. |
| Control description | Management performs periodic analysis of complete active user entitlement populations against the approved segregation of duties matrix and remediates or formally mitigates identified conflicts. |
| Objective | Incompatible duties within and across in scope systems are identified, prevented, remediated, or mitigated through approved compensating controls. |
| Population | All active human, privileged, generic, and applicable service accounts with roles and permissions across in scope systems. |
| Frequency | Weekly detective monitoring; formal management review at least quarterly. |
| Control owner | Financial Systems Controls |
| Nature | Automated detection with response and closure owned by humans. |

## Control activities

1. Collect authoritative account and entitlement populations from every in scope application for the same review cutoff.
2. Validate source identity, collection method, query, period, schema, row count, uniqueness, and SHA-256 fingerprint.
3. Reconcile every entitlement to an application account and common user identifier. Stop the run if the population cannot be reconciled.
4. Confirm that the deployed SoD rules are approved, effective, and match the authorized matrix version.
5. Reconcile the business process risk inventory to the matrix so risks across applications cannot silently fall outside monitoring.
6. Evaluate each active identity against all applicable rule pairs within and across applications.
7. For each conflict, validate the exception owner, approval, expiry, reassessment date, compensating control identifier, latest test result, evidence, and independent review.
8. Route each unsupported finding to a human owner. Retain access change, lookback, root cause, approval, and closure evidence.

## Rule to risk mapping

| Rule | Failure addressed | Evidence |
|---|---|---|
| SOD-01 | Stale, unapproved, or wrongly deployed conflict logic | Matrix version, approver, effective dates, evaluation for each rule |
| SOD-02 | Active identity can perform incompatible duties without effective mitigation | Account and entitlement records, matched rule, exception assessment |
| SOD-03 | A process risk across systems is absent from the matrix | Reconciliation of the process risk inventory to the approved matrix |
| SOD-04 | Accepted conflict lacks current governance or an operating control | Exception approval, owner, expiry, reassessment, and control test evidence |

## Completeness and accuracy

Completeness is established at two levels. Source files must match the manifest metadata, and entitlements must reconcile to the account population. Matrix completeness is assessed separately by comparing approved rules to the business process risk inventory. Accuracy is supported by deterministic matching on application, entitlement, account, and user identifiers and by retaining the exact source fingerprints used by the run.

The proof of concept does not claim production completeness. A production implementation must reconcile collector results to each application's authoritative inventory and document expected exclusions, including treatment of accounts that do not belong to a person.
