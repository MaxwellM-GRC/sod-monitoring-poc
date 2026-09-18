# SoD exception SOD-586a0d9ecf1b7f0c

- **Run ID:** `RUN-3cb95278b2b81920`
- **Control / rule:** `ITGC-SOD-001` / `SOD-02`
- **Severity:** critical
- **Conflict rule:** `SOD-R001`
- **User / object:** `u100` — Maya Chen
- **Accounts:** ATL-100 | ERP-100
- **Applications:** atlas_treasury | coranto_erp
- **Entitlements:** coranto_erp:VENDOR_MAINTAIN | atlas_treasury:PAYMENT_RELEASE
- **Existing exception:** `none`
- **Status:** Open — human decision required

## Control assertion

No active user holds an unmitigated incompatible access combination.

## Risk and detection detail

A user could create or alter a vendor and release payment to that vendor

Active incompatible access is not effectively mitigated: no approved exception.

## Human approved response

- [ ] Accountable owner assigned.
- [ ] Management chose and approved access removal, role redesign, or a time bound compensating control: Remove or redesign one side of the conflicting access, or obtain formal approval for a time bound compensating control.
- [ ] Exposure period analysis completed: Review relevant transactions during the exposure period and validate that an independent control detected or prevented inappropriate activity.
- [ ] Root cause documented: Determine whether role design, provisioning bypass, matrix mapping, system integration, or periodic review failed.
- [ ] Closure package attached: Entitlement evidence from before and after the change, an approved exception if applicable, the transaction lookback, and control owner approval.
- [ ] Escalation requirement assessed: Escalate immediately for conflicts capable of creating and approving or releasing financial transactions without independent review.
- [ ] Closure approved by `Financial Systems Controls` or an authorized delegate.

## Decision record

| Field | Human entry |
|---|---|
| Response owner | |
| Decision and rationale | |
| Approved by / date | |
| Remediation completed at | |
| Lookback conclusion | |
| Closure evidence links | |
| Closure approved by / date | |

Automation may detect, route, and recommend. It must not remove access, accept
risk, attest that a compensating control operated, or close this case.
