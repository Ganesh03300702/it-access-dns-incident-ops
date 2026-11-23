# KB-04: Server SSH (Port 22) & RDP (Port 3389) Connectivity Troubleshooting

Guides L1 engineers through diagnosing remote server login failures.

## Troubleshooting Sequence
1. **Port Check:** `Test-NetConnection <server-ip> -Port 22` (SSH) or `-Port 3389` (RDP).
2. **Verify DNS vs. IP:** Test direct IP login to rule out DNS mismatch.
3. **Service Status:** Linux `sudo systemctl status sshd` | Windows `Get-Service TermService`.
4. **Firewall & Account Lockout:** Check `ufw`/`firewall-cmd` or Windows Firewall rules and verify account is not locked out in Active Directory.
