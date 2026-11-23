import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from config import DEFAULT_DB_PATH


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS ad_users (
                username TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                department TEXT NOT NULL,
                ou_path TEXT NOT NULL,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ad_group_memberships (
                username TEXT NOT NULL,
                security_group TEXT NOT NULL,
                granted_at TEXT NOT NULL,
                PRIMARY KEY (username, security_group)
            );

            CREATE TABLE IF NOT EXISTS access_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                request_id TEXT NOT NULL,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                security_group TEXT NOT NULL,
                approved_by TEXT NOT NULL,
                outcome TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS network_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                check_type TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                details TEXT
            );

            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_to TEXT NOT NULL,
                rca TEXT DEFAULT '',
                kb_reference TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS kb_articles (
                kb_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                file_path TEXT NOT NULL,
                summary TEXT NOT NULL
            );
            """
        )


def query_all(sql: str, params: tuple = (), db_path: Path = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
