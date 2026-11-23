import argparse
import json
from pathlib import Path

from access_manager import list_active_users, process_access_requests_csv
from incident_kb import (
    create_incident,
    list_incidents,
    resolve_incident,
    search_kb,
    sync_kb_articles,
)
from network_diag import run_network_diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="IT Access Provisioning (AD/RBAC), DNS/DHCP Diagnostics & Incident KB CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_acc = sub.add_parser("provision", help="Process AD/RBAC user access CSV")
    p_acc.add_argument("--csv", type=Path, default=Path("sample_access_requests.csv"))

    sub.add_parser("users", help="List AD users and security groups")

    p_net = sub.add_parser("netcheck", help="Run DNS, DHCP/IP, and TCP port diagnostics")
    p_net.add_argument("--skip-external", action="store_true", help="Only run local IP/DHCP check")

    sub.add_parser("sync-kb", help="Index Markdown KB articles into SQLite")

    p_kb = sub.add_parser("search-kb", help="Search Knowledge Base articles")
    p_kb.add_argument("keyword", type=str)

    p_inc = sub.add_parser("open-incident", help="Create a new L1 incident ticket")
    p_inc.add_argument("--title", required=True)
    p_inc.add_argument("--category", default="Networking")
    p_inc.add_argument("--severity", default="P2", choices=["P1", "P2", "P3"])

    p_res = sub.add_parser("resolve-incident", help="Resolve an incident with RCA & KB link")
    p_res.add_argument("--ticket", required=True)
    p_res.add_argument("--rca", required=True)
    p_res.add_argument("--kb", default="")

    sub.add_parser("incidents", help="List all tracked incidents")

    args = parser.parse_args()

    if args.command == "provision":
        print(json.dumps(process_access_requests_csv(args.csv), indent=2))
    elif args.command == "users":
        print(json.dumps(list_active_users(), indent=2))
    elif args.command == "netcheck":
        print(json.dumps(run_network_diagnostics(skip_external=args.skip_external), indent=2))
    elif args.command == "sync-kb":
        print(json.dumps({"indexed_kb_articles": sync_kb_articles()}, indent=2))
    elif args.command == "search-kb":
        sync_kb_articles()
        print(json.dumps(search_kb(args.keyword), indent=2))
    elif args.command == "open-incident":
        print(json.dumps(create_incident(args.title, args.category, args.severity), indent=2))
    elif args.command == "resolve-incident":
        ok = resolve_incident(args.ticket, args.rca, args.kb)
        print(json.dumps({"ticket_id": args.ticket, "resolved": ok}, indent=2))
    elif args.command == "incidents":
        print(json.dumps(list_incidents(), indent=2))


if __name__ == "__main__":
    main()
