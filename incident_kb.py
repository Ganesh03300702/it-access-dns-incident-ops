from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from config import DEFAULT_DB_PATH, DEFAULT_KB_DIR
from db import get_connection, init_db, query_all


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sync_kb_articles(kb_dir: Path = DEFAULT_KB_DIR, db_path: Path = DEFAULT_DB_PATH) -> int:
    init_db(db_path)
    count = 0
    if not kb_dir.exists():
        return 0

    with get_connection(db_path) as conn:
        for md_file in sorted(kb_dir.glob("*.md")):
            lines = [ln.strip() for ln in md_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
            title = lines[0].lstrip("# ").strip() if lines else md_file.stem
            parts = md_file.stem.split("-")
            kb_id = f"{parts[0]}-{parts[1]}" if len(parts) >= 2 else md_file.stem
            category = "Networking" if any(k in title.lower() for k in ("dns", "dhcp", "ssh", "rdp")) else "Access & IAM"
            summary = next((ln for ln in lines[1:] if not ln.startswith("#") and not ln.startswith("-")), title)

            conn.execute(
                """
                INSERT INTO kb_articles (kb_id, title, category, file_path, summary)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(kb_id) DO UPDATE SET
                    title=excluded.title,
                    category=excluded.category,
                    file_path=excluded.file_path,
                    summary=excluded.summary
                """,
                (kb_id.upper(), title, category, str(md_file), summary[:220]),
            )
            count += 1
    return count


def search_kb(keyword: str, db_path: Path = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    like = f"%{keyword.lower()}%"
    return query_all(
        """
        SELECT kb_id, title, category, file_path, summary
        FROM kb_articles
        WHERE LOWER(title) LIKE ? OR LOWER(category) LIKE ? OR LOWER(summary) LIKE ?
        ORDER BY kb_id
        """,
        (like, like, like),
        db_path=db_path,
    )


def create_incident(
    title: str,
    category: str,
    severity: str = "P3",
    assigned_to: str = "Ops-L1",
    db_path: Path = DEFAULT_DB_PATH,
) -> Dict[str, Any]:
    init_db(db_path)
    severity = severity.upper()
    if severity not in {"P1", "P2", "P3"}:
        raise ValueError("Severity must be P1, P2, or P3")

    ts = utc_now()
    with get_connection(db_path) as conn:
        next_num = conn.execute("SELECT COUNT(*) + 1001 AS n FROM incidents").fetchone()["n"]
        ticket_id = f"INC-{next_num}"
        conn.execute(
            """
            INSERT INTO incidents (ticket_id, created_at, title, category, severity, status, assigned_to)
            VALUES (?, ?, ?, ?, ?, 'OPEN', ?)
            """,
            (ticket_id, ts, title, category, severity, assigned_to),
        )
    return {
        "ticket_id": ticket_id,
        "created_at": ts,
        "title": title,
        "category": category,
        "severity": severity,
        "status": "OPEN",
        "assigned_to": assigned_to,
    }


def resolve_incident(
    ticket_id: str,
    rca: str,
    kb_reference: str = "",
    db_path: Path = DEFAULT_DB_PATH,
) -> bool:
    init_db(db_path)
    with get_connection(db_path) as conn:
        cur = conn.execute(
            """
            UPDATE incidents
            SET status = 'RESOLVED', rca = ?, kb_reference = ?
            WHERE ticket_id = ?
            """,
            (rca, kb_reference, ticket_id),
        )
        return cur.rowcount > 0


def list_incidents(db_path: Path = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    init_db(db_path)
    return query_all("SELECT * FROM incidents ORDER BY id DESC", db_path=db_path)
