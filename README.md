# IT Access Provisioning, DNS Diagnostics & Incident KB Hub

An entry-level **IT Infrastructure & Active Directory Operations** automation hub built with **Python, PowerShell, Bash, and SQLite**.

## Key Features
- **AD / RBAC User Access Provisioning:** Processes CSV requests (`GRANT`/`REVOKE`), maps roles to AD Security Groups and OUs, disables accounts upon full revocation, and logs an immutable audit trail in **SQLite**. Includes a PowerShell AD script (`Invoke-ADUserProvisioning.ps1`) with safe `-DryRun` simulation mode.
- **DNS, DHCP & Port Diagnostics:** Verifies DNS `A`-record lookup latency, detects DHCP/APIPA (`169.254.x.x`) failures, and checks critical TCP ports (`53`, `443`, `22`, `3389`). Includes PowerShell (`Test-DnsDhcpHealth.ps1`) and Bash (`network_diagnostics.sh`) utilities.
- **L1 Incident Ticketing & Searchable KB:** CLI to open `P1/P2/P3` tickets, resolve incidents with RCA + KB links, and search indexed Markdown troubleshooting guides.
- **Practical L1 KB Articles (`kb-articles/`):** 4 guides covering DNS triage, DHCP/APIPA recovery, AD user access SOPs, and SSH/RDP connectivity.

## Project Structure
```text
it-access-dns-incident-ops/
├── .github/workflows/ci.yml   # GitHub Actions CI (PyTest + Bash lint)
├── kb-articles/               # L1 Troubleshooting KB Guides
├── scripts/
│   ├── linux/                 # Bash DNS & interface diagnostics
│   └── windows/               # PowerShell AD provisioning & DNS/DHCP health
├── tests/                     # Automated PyTest suite
├── .env.example
├── .gitignore
├── access_manager.py
├── cli.py                     # Main unified CLI
├── config.py
├── db.py
├── incident_kb.py
├── network_diag.py
├── network_targets.json
├── README.md
├── requirements.txt
├── sample_access_requests.csv
└── TEST_PLAN.md
```

## Quick Start
```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux / WSL:
source .venv/bin/activate

pip install -r requirements.txt
python cli.py provision --csv sample_access_requests.csv
python cli.py users
python cli.py netcheck
python cli.py search-kb dns
pytest -v
```
