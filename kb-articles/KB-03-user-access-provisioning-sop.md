# KB-03: Standard User Access Provisioning & Offboarding SOP (Active Directory)

Defines the least-privilege process for handling IT user access requests and timely revocations.

## Provisioning Checklist (GRANT)
1. Confirm ticket contains **Manager / System Owner approval** (`approved_by` field cannot be blank).
2. Map requested role to approved AD Security Group:
   - `Ops-L1` -> `SG-Platform-Ops-L1`
   - `Developer-ReadOnly` -> `SG-Dev-ReadOnly`
   - `AD-Admin-Temp` -> `SG-IT-Temp-Admin`
3. Execute via `python cli.py provision --csv sample_access_requests.csv` or `Invoke-ADUserProvisioning.ps1`.

## Offboarding Checklist (REVOKE)
1. Remove user from security groups upon role transfer or exit.
2. Disable the AD account once all group memberships are revoked (`status = DISABLED`); retain for audit compliance.
