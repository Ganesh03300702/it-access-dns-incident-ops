import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from config import DEFAULT_DB_PATH, DEFAULT_DOMAIN_DN
from db import get_connection, init_db, query_all


ROLE_TO_AD_GROUP = {
    "Ops-L1": "SG-Platform-Ops-L1",
    "Developer-ReadOnly": "SG-Dev-ReadOnly",
    "AD-Admin-Temp": "SG-IT-Temp-Admin",
    "Analytics-Viewer": "SG-Analytics-Viewers",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def process_access_requests_csv(
    csv_path: Path,
    domain_dn: str = DEFAULT_DOMAIN_DN,
    db_path: Path = DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    init_db(db_path)
    results: List[Dict[str, Any]] = []

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        with get_connection(db_path) as conn:
            for row in reader:
                ts = utc_now()
                req_id = row["request_id"].strip()
                username = row["username"].strip().lower()
                full_name = row["full_name"].strip()
                department = row["department"].strip()
                role = row["role"].strip()
                action = row["action"].strip().upper()
                approved_by = row["approved_by"].strip()

                sec_group = ROLE_TO_AD_GROUP.get(role, "SG-General-Users")
                ou_path = f"OU={department},{domain_dn}"

                if not approved_by:
                    outcome = "REJECTED_NO_APPROVER"
                elif action == "GRANT":
                    conn.execute(
                        """
                        INSERT INTO ad_users (username, full_name, department, ou_path, status, updated_at)
                        VALUES (?, ?, ?, ?, 'ACTIVE', ?)
                        ON CONFLICT(username) DO UPDATE SET
                            department=excluded.department,
                            ou_path=excluded.ou_path,
                            status='ACTIVE',
                            updated_at=excluded.updated_at
                        """,
                        (username, full_name, department, ou_path, ts),
                    )
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO ad_group_memberships (username, security_group, granted_at)
                        VALUES (?, ?, ?)
                        """,
                        (username, sec_group, ts),
                    )
                    outcome = "GRANTED"
                elif action == "REVOKE":
                    conn.execute(
                        "DELETE FROM ad_group_memberships WHERE username = ? AND security_group = ?",
                        (username, sec_group),
                    )
                    remaining = conn.execute(
                        "SELECT COUNT(*) AS cnt FROM ad_group_memberships WHERE username = ?",
                        (username,),
                    ).fetchone()["cnt"]
                    if remaining == 0:
                        conn.execute(
                            "UPDATE ad_users SET status = 'DISABLED', updated_at = ? WHERE username = ?",
                            (ts, username),
                        )
                    outcome = "REVOKED"
                else:
                    outcome = "INVALID_ACTION"

                conn.execute(
                    """
                    INSERT INTO access_audit_log
                    (timestamp, request_id, username, action, security_group, approved_by, outcome)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (ts, req_id, username, action, sec_group, approved_by, outcome),
                )

                results.append({
                    "request_id": req_id,
                    "username": username,
                    "action": action,
                    "security_group": sec_group,
                    "ou_path": ou_path,
                    "outcome": outcome,
                })

    return results


def list_active_users(db_path: Path = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    return query_all(
        """
        SELECT u.username, u.full_name, u.department, u.ou_path, u.status,
               COALESCE(GROUP_CONCAT(g.security_group, ', '), '') AS groups
        FROM ad_users u
        LEFT JOIN ad_group_memberships g ON u.username = g.username
        GROUP BY u.username
        ORDER BY u.username
        """,
        db_path=db_path,
    )
