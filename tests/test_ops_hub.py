import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from access_manager import list_active_users, process_access_requests_csv
from incident_kb import create_incident, list_incidents, resolve_incident, search_kb, sync_kb_articles
from network_diag import run_network_diagnostics


def test_ad_provisioning_grant_and_revoke(tmp_path: Path):
    db_file = tmp_path / "ops_test.db"
    results = process_access_requests_csv(
        ROOT / "sample_access_requests.csv", db_path=db_file
    )
    assert len(results) == 5

    users = {u["username"]: u for u in list_active_users(db_path=db_file)}
    assert users["arjun.mehta"]["status"] == "ACTIVE"
    assert "SG-Platform-Ops-L1" in users["arjun.mehta"]["groups"]
    assert users["rohan.verma"]["status"] == "DISABLED"
    assert users["rohan.verma"]["groups"] == ""


def test_kb_sync_and_incident_lifecycle(tmp_path: Path):
    db_file = tmp_path / "ops_test.db"
    count = sync_kb_articles(ROOT / "kb-articles", db_path=db_file)
    assert count == 4

    dns_hits = search_kb("dns", db_path=db_file)
    assert len(dns_hits) >= 1

    ticket = create_incident("DNS timeout on app-02", "Networking", "P2", db_path=db_file)
    assert ticket["ticket_id"].startswith("INC-")
    assert resolve_incident(ticket["ticket_id"], "Flushed stale resolver cache", "KB-01", db_path=db_file)

    all_inc = list_incidents(db_path=db_file)
    assert all_inc[0]["status"] == "RESOLVED"
    assert all_inc[0]["kb_reference"] == "KB-01"


def test_local_network_diagnostics(tmp_path: Path):
    db_file = tmp_path / "ops_test.db"
    res = run_network_diagnostics(
        config_path=ROOT / "network_targets.json",
        db_path=db_file,
        skip_external=True,
    )
    assert len(res) == 1
    assert res[0]["check_type"] == "DHCP_IP"
