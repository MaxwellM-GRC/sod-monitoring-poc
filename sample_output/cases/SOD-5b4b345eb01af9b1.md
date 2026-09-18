# SoD exception SOD-5b4b345eb01af9b1

- **Run ID:** `RUN-3cb95278b2b81920`
- **Control / rule:** `ITGC-SOD-001` / `SOD-04`
- **Severity:** high
- **Conflict rule:** `SOD-R001`
- **User / object:** `u400` — Jordan Bell
- **Accounts:** ATL-400 | ERP-400
- **Applications:** atlas_treasury | coranto_erp
- **Entitlements:** coranto_erp:VENDOR_MAINTAIN | atlas_treasury:PAYMENT_RELEASE
- **Existing exception:** `EXC-400`
- **Status:** Open — human decision required

## Control assertion

Accepted conflicts have a current owner, approval, compensating control, and periodic reassessment.

## Risk and detection detail

A user could create or alter a vendor and release payment to that vendor

Accepted conflict governance is not current or effective: latest compensating control test result is failed.

## Human approved response

- [ ] Accountable owner assigned.
- [ ] Management chose and approved access removal, role redesign, or a time bound compensating control: Remove conflicting access or renew and approve the exception with an owned, effective compensating control and reassessment date.
- [ ] Exposure period analysis completed: Perform the overdue or failed compensating control review and a transaction lookback for the unsupported period.
- [ ] Root cause documented: Determine why exception ownership, expiry monitoring, evidence collection, or control performance failed.
- [ ] Closure package attached: Current approval, owner, compensating control test, reassessment date, lookback conclusion, and control owner approval.
- [ ] Escalation requirement assessed: Escalate immediately when a critical conflict has no effective compensating control; otherwise at the response SLA.
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
