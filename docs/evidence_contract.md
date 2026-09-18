# Evidence contract

## Source manifest

Every configured source must have exactly one manifest entry with:

- stable source identifier and fictional or production source URI;
- extraction method and query/filter description;
- UTC extraction timestamp and common review window;
- expected row count; and
- SHA-256 fingerprint of the collected file.

The evaluator fails closed for a missing source, manifest mismatch, blank provenance field, missing required column, duplicate configured key, changed hash, wrong period, orphan entitlement, or account/user mismatch.

## Evidence package

`control_evidence.json` is the primary machine readable run artifact. It records the control definition, review parameters, source checks, population counts, matrix version tests, process risk coverage, all detected conflicts, effective mitigations, findings, and stable identifiers for runs and findings.

`exceptions.csv` is designed for an RCM or GRC import. Each row contains the control assertion, severity, affected identity and accounts, applications, entitlements, risk, detection detail, existing exception, response guidance, and intentionally blank fields for the management decision and closure.

`cases/` contains one human readable case per finding. The case includes a response checklist and decision record table. Case identifiers are deterministic for the same control, rule, and affected object so monitoring can update rather than duplicate a case.

## Retention and reperformance

A production evidence store should retain the immutable input extracts, source manifest, exact approved configuration, generated evidence, workflow identity, code revision, human response records, and closure approval under the organization's retention policy. The deterministic run ID is derived from the configuration and source fingerprints; it identifies the evidence set, not the execution timestamp.
