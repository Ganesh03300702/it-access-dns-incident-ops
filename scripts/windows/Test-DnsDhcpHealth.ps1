<#
.SYNOPSIS
    Runs Windows DNS resolution, DHCP lease inspection, and TCP port connectivity checks.
.EXAMPLE
    .\scripts\windows\Test-DnsDhcpHealth.ps1
#>
param(
    [string[]]$Domains = @("google.com", "github.com", "cloudflare.com")
)

Write-Host "=== 1. DHCP & IPv4 Interface Summary ===" -ForegroundColor Cyan
Get-NetIPConfiguration | Where-Object { $_.IPv4Address -ne $null } | ForEach-Object {
    $iface = Get-NetIPInterface -InterfaceIndex $_.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    [PSCustomObject]@{
        Interface  = $_.InterfaceAlias
        IPv4       = $_.IPv4Address.IPAddress
        Gateway    = ($_.IPv4DefaultGateway.NextHop -join ", ")
        DNSServers = ($_.DNSServer.ServerAddresses -join ", ")
        DHCP       = $iface.Dhcp
    }
} | Format-Table -AutoSize

Write-Host "=== 2. DNS Resolution Checks ===" -ForegroundColor Cyan
foreach ($domain in $Domains) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $res = Resolve-DnsName -Name $domain -Type A -ErrorAction Stop | Select-Object -First 1
        $sw.Stop()
        Write-Host ("[OK]   {0,-18} -> {1,-16} ({2} ms)" -f $domain, $res.IPAddress, $sw.ElapsedMilliseconds) -ForegroundColor Green
    } catch {
        $sw.Stop()
        Write-Host ("[FAIL] {0,-18} -> Resolution failed: {1}" -f $domain, $_.Exception.Message) -ForegroundColor Red
    }
}

Write-Host "=== 3. Key Infrastructure Port Checks ===" -ForegroundColor Cyan
$targets = @(
    @{ Host = "8.8.8.8"; Port = 53; Label = "DNS" },
    @{ Host = "github.com"; Port = 443; Label = "HTTPS" }
)
foreach ($t in $targets) {
    $conn = Test-NetConnection -ComputerName $t.Host -Port $t.Port -WarningAction SilentlyContinue
    $state = if ($conn.TcpTestSucceeded) { "OPEN" } else { "CLOSED/BLOCKED" }
    Write-Host ("[{0}] {1}:{2} ({3})" -f $state, $t.Host, $t.Port, $t.Label)
}
