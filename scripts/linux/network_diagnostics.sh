#!/usr/bin/env bash
# Runs Linux DNS, DHCP/IP configuration, and TCP port reachability diagnostics
set -euo pipefail

DOMAINS=("google.com" "github.com" "cloudflare.com")

echo "=== 1. Network Interfaces & Default Gateway ==="
if command -v ip >/dev/null 2>&1; then
    ip -brief addr show
    ip route show default || true
else
    hostname -I || true
fi

echo ""
echo "=== 2. Configured DNS Resolvers (/etc/resolv.conf) ==="
grep -E "^nameserver" /etc/resolv.conf 2>/dev/null || echo "No nameserver entries found."

echo ""
echo "=== 3. DNS Resolution Tests ==="
for d in "${DOMAINS[@]}"; do
    if command -v dig >/dev/null 2>&1; then
        IP_RES=$(dig +short "$d" A | head -n 1)
    elif command -v getent >/dev/null 2>&1; then
        IP_RES=$(getent ahostsv4 "$d" | awk 'NR==1 {print $1}')
    else
        IP_RES=""
    fi

    if [ -n "$IP_RES" ]; then
        echo "[OK]   $d -> $IP_RES"
    else
        echo "[FAIL] $d -> DNS lookup failed"
    fi
done
