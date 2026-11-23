# KB-02: DHCP Lease Failure & APIPA (169.254.x.x) Recovery

Fixes workstations or servers failing to obtain a valid IPv4 address from the DHCP server.

## Symptoms
- Host displays an IP address in `169.254.0.0/16` (APIPA).
- No default gateway listed; zero network or internet connectivity.

## Step-by-Step Troubleshooting
1. **Confirm current lease state:** Windows `ipconfig /all` or Linux `ip addr show`.
2. **Release and renew lease:**
   - Windows: `ipconfig /release && ipconfig /renew`
   - Linux: `sudo dhclient -r && sudo dhclient`
3. **Check link & DHCP scope:** If multiple machines on the same subnet receive APIPA, suspect **DHCP Scope Exhaustion** or DHCP Relay outage and escalate immediately.
