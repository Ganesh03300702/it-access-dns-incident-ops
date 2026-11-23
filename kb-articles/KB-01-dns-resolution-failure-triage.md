# KB-01: DNS Resolution Failure Triage Guide

Resolves intermittent or complete hostname lookup failures across Linux and Windows servers.

## Symptoms
- Application logs report `Name or service not known` or `Temporary failure in name resolution`.
- Ping by IP works (`ping 8.8.8.8`), but ping by hostname fails (`ping github.com`).

## Step-by-Step Troubleshooting
1. **Verify configured DNS servers:**
   - Windows: `ipconfig /all` or `Get-DnsClientServerAddress`
   - Linux: `cat /etc/resolv.conf` or `resolvectl status`
2. **Test direct resolution:**
   - Windows: `nslookup internal.corp.local` / `Resolve-DnsName github.com`
   - Linux: `dig github.com +stats` / `nslookup github.com`
3. **Flush DNS Cache:**
   - Windows: `ipconfig /flushdns`
   - Linux: `sudo resolvectl flush-caches`
4. **Verify Port 53 reachability:** `Test-NetConnection <DNS_IP> -Port 53` or `nc -zv <DNS_IP> 53`

## Escalation
If local config is clean and TCP/UDP 53 to primary DNS times out across multiple hosts, open a **P1/P2** ticket for Network/DNS Engineering.
