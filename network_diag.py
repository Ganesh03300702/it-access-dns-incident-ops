import json
import platform
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from config import DEFAULT_DB_PATH, DEFAULT_NETWORK_TARGETS
from db import get_connection, init_db


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_dns_resolution(domains: List[str]) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for domain in domains:
        start = time.perf_counter()
        try:
            ip_addr = socket.gethostbyname(domain)
            latency = round((time.perf_counter() - start) * 1000.0, 2)
            results.append({
                "timestamp": utc_now(),
                "check_type": "DNS_A",
                "target": domain,
                "status": "PASS",
                "latency_ms": latency,
                "details": f"Resolved to {ip_addr}",
            })
        except socket.gaierror as exc:
            latency = round((time.perf_counter() - start) * 1000.0, 2)
            results.append({
                "timestamp": utc_now(),
                "check_type": "DNS_A",
                "target": domain,
                "status": "FAIL",
                "latency_ms": latency,
                "details": f"DNS failure: {exc}",
            })
    return results


def check_tcp_ports(targets: List[Dict[str, Any]], timeout: float = 2.0) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for item in targets:
        start = time.perf_counter()
        host = item["host"]
        port = int(item["port"])
        try:
            with socket.create_connection((host, port), timeout=timeout):
                status = "PASS"
                details = f"{item['name']} port {port} reachable"
        except OSError as exc:
            status = "FAIL"
            details = f"{item['name']} port {port} unreachable ({exc.__class__.__name__})"
        latency = round((time.perf_counter() - start) * 1000.0, 2)
        results.append({
            "timestamp": utc_now(),
            "check_type": "TCP_PORT",
            "target": f"{host}:{port}",
            "status": status,
            "latency_ms": latency,
            "details": details,
        })
    return results


def inspect_local_dhcp_ip() -> Dict[str, Any]:
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except OSError:
        local_ip = "127.0.0.1"

    apipa_warning = local_ip.startswith("169.254.")
    os_type = platform.system()
    dhcp_note = "APIPA detected (DHCP lease failure!)" if apipa_warning else "Valid IPv4 assigned"

    cmd = ["ipconfig", "/all"] if os_type == "Windows" else ["ip", "-brief", "addr"]
    snippet = ""
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=False)
        snippet = proc.stdout.strip()[:300]
    except Exception:
        snippet = "Local interface command unavailable"

    return {
        "timestamp": utc_now(),
        "check_type": "DHCP_IP",
        "target": hostname,
        "status": "FAIL" if apipa_warning else "PASS",
        "latency_ms": 0.0,
        "details": f"IP={local_ip} | {dhcp_note}",
        "raw_preview": snippet,
    }


def run_network_diagnostics(
    config_path: Path = DEFAULT_NETWORK_TARGETS,
    db_path: Path = DEFAULT_DB_PATH,
    skip_external: bool = False,
) -> List[Dict[str, Any]]:
    init_db(db_path)
    cfg = json.loads(config_path.read_text(encoding="utf-8"))

    results: List[Dict[str, Any]] = [inspect_local_dhcp_ip()]
    if not skip_external:
        results.extend(check_dns_resolution(cfg.get("dns_domains", [])))
        results.extend(check_tcp_ports(cfg.get("service_ports", [])))

    with get_connection(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO network_checks (timestamp, check_type, target, status, latency_ms, details)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (r["timestamp"], r["check_type"], r["target"], r["status"], r["latency_ms"], r["details"])
                for r in results
            ],
        )

    return results
