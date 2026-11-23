# Test & Verification Plan

## 1. Automated Unit & Integration Tests
```bash
pytest -v
```
Expected: All 3 tests pass (`test_ad_provisioning_grant_and_revoke`, `test_kb_sync_and_incident_lifecycle`, `test_local_network_diagnostics`).

## 2. End-to-End CLI Smoke Tests
```bash
python cli.py provision --csv sample_access_requests.csv
python cli.py users
python cli.py netcheck
python cli.py sync-kb
python cli.py search-kb dns
python cli.py open-incident --title "DNS resolution timeout on web-01" --severity P2
python cli.py resolve-incident --ticket INC-1001 --rca "Flushed stale DNS cache" --kb KB-01
python cli.py incidents
```
Verify:
- `rohan.verma` shows `DISABLED` after revocation, while `arjun.mehta` shows `ACTIVE` in `SG-Platform-Ops-L1`.
- `netcheck` prints local DHCP/IP check, DNS resolution latencies, and TCP port states.
- `INC-1001` transitions cleanly from `OPEN` to `RESOLVED` linked to `KB-01`.

## 3. Native OS Script Verification
- **Windows PowerShell:**
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\scripts\windows\Invoke-ADUserProvisioning.ps1 -CsvPath .\sample_access_requests.csv -DryRun
  .\scripts\windows\Test-DnsDhcpHealth.ps1
  ```
- **Linux / WSL Bash:**
  ```bash
  bash -n scripts/linux/*.sh
  chmod +x scripts/linux/*.sh
  ./scripts/linux/network_diagnostics.sh
  ```
