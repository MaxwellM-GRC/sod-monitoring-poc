# Human approved response runbook

Automation provides a recommendation, not authorization. The accountable owner must review the identity, entitlement lineage, matrix rule, business purpose, and source evidence before changing access or accepting risk.

## Response path

1. **Triage.** Confirm the user/account correlation and whether both entitlements remained active at the review cutoff. Escalate immediately when the conflict can create and approve or release a financial transaction.
2. **Contain and decide.** The system owner and business process owner choose access removal, role redesign, or a documented, time bound exception. Access removal should follow the approved access change process.
3. **Look back.** Review transactions and relevant changes to master data for the actual exposure period. Scope the procedures to the conflict risk; for example, match vendor changes to released payments for SOD-R001.
4. **Mitigate if retained.** Name an accountable owner, authorized approver, control activity, evidence source, performer, independent reviewer, frequency, expiry, and reassessment date. A failed or missing control test does not support the exception.
5. **Correct root cause.** Address role design, provisioning, identity correlation, matrix coverage, system integration, or exception monitoring as applicable.
6. **Close.** Attach before/after access, approved exception or removal, lookback conclusion, control evidence, root cause, and management approval. A human control owner approves closure.

## Recurrence and escalation

A recurring finding retains its stable finding ID and updates the same open exception case. The response owner assesses whether recurrence changes the root cause, lookback scope, remediation plan, or risk decision. Recurrence does not reset the response SLA or provide a basis for automatic closure.

Open cases that exceed the five day response SLA receive the `sla-breached` label and an escalation comment for Financial Systems Controls. Critical conflicts that can create and approve or release a financial transaction require immediate escalation rather than waiting for the SLA.

The workflow must not interpret a conflict's absence from a later extract as closure. It adds `human-closure-review` so the owner can verify that remediation, lookback, and evidence requirements are satisfied.
