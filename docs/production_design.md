# Production design considerations

## Collection and identity

Replace static CSVs with collectors that use read only, least privilege access to identity governance, ERP, treasury, expense, billing, and GRC services. Store immutable extracts before normalization. Reconcile each collector to an authoritative application inventory, use a governed person and account correlation key, and explicitly document whether service and generic accounts apply.

## Cloud native execution

Run the containerized evaluator on an approved schedule with workload identity rather than credentials that remain valid for a long period. Encrypt source and output evidence, restrict evidence access, log collector and workflow activity, pin build dependencies, sign releases, and retain the code revision and configuration digest with every run. A queue can route findings to the GRC or ticketing platform while preserving stable case identifiers.

## Rule and exception governance

Maintain the SoD matrix as a versioned, approved configuration with protected changes and effective dates. Reconcile the matrix to business process risk analysis and application scope after implementations, role redesigns, acquisitions, or material process changes. Approved exceptions should have separate ownership, approval, expiry, reassessment, and compensating control evidence; access administrators must not approve their own exceptions.

## Safety boundary

Production automation may collect, detect, prioritize, and route. It should not remove access, redesign roles, approve an exception, attest control performance, or close a case without an authorized human decision. Separate monitoring credentials from access administration credentials and make response actions reversible where feasible.

## Deployment gates

Before production use, validate source completeness for every in scope system, confirm identity correlation accuracy, run user acceptance tests for every matrix rule, tune known false positives, define response and escalation SLAs, verify evidence retention, test failure alerts, perform security review, and obtain control owner approval.
