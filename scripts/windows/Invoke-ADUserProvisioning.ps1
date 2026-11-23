<#
.SYNOPSIS
    Automates Active Directory user onboarding, security group assignment, and offboarding from CSV.
    Runs safely in Simulation Mode (-DryRun) on workstations without RSAT/ActiveDirectory module.
.EXAMPLE
    .\scripts\windows\Invoke-ADUserProvisioning.ps1 -CsvPath ".\sample_access_requests.csv" -DryRun
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$CsvPath,
    [string]$DomainBaseDN = "DC=corp,DC=local",
    [switch]$DryRun
)

if (-not (Test-Path $CsvPath)) {
    Write-Error "CSV file not found: $CsvPath"
    exit 1
}

$hasADModule = $null -ne (Get-Module -ListAvailable -Name ActiveDirectory)
if (-not $hasADModule -and -not $DryRun) {
    Write-Warning "ActiveDirectory RSAT module not detected. Automatically switching to -DryRun simulation mode."
    $DryRun = $true
}

$roleToGroupMap = @{
    "Ops-L1"             = "SG-Platform-Ops-L1"
    "Developer-ReadOnly" = "SG-Dev-ReadOnly"
    "AD-Admin-Temp"      = "SG-IT-Temp-Admin"
    "Analytics-Viewer"   = "SG-Analytics-Viewers"
}

$requests = Import-Csv -Path $CsvPath
$auditLog = @()

foreach ($req in $requests) {
    $groupName = if ($roleToGroupMap.ContainsKey($req.role)) { $roleToGroupMap[$req.role] } else { "SG-General-Users" }
    $ouPath = "OU=$($req.department),$DomainBaseDN"
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

    if ($req.action -eq "GRANT") {
        if ($DryRun) {
            Write-Host "[$timestamp] [DRY-RUN] Would create/enable AD user '$($req.username)' in '$ouPath' and add to group '$groupName' (Approved by: $($req.approved_by))"
        } else {
            $existing = Get-ADUser -Filter "SamAccountName -eq '$($req.username)'" -ErrorAction SilentlyContinue
            if (-not $existing) {
                New-ADUser -Name $req.full_name -SamAccountName $req.username -Department $req.department -Path $ouPath -Enabled $true
            }
            Add-ADGroupMember -Identity $groupName -Members $req.username
        }
        $status = if ($DryRun) { "SIMULATED_GRANT" } else { "GRANTED" }
    } elseif ($req.action -eq "REVOKE") {
        if ($DryRun) {
            Write-Host "[$timestamp] [DRY-RUN] Would remove '$($req.username)' from group '$groupName' and log revocation."
        } else {
            Remove-ADGroupMember -Identity $groupName -Members $req.username -Confirm:$false
        }
        $status = if ($DryRun) { "SIMULATED_REVOKE" } else { "REVOKED" }
    } else {
        $status = "INVALID_ACTION"
    }

    $auditLog += [PSCustomObject]@{
        timestamp  = $timestamp
        request_id = $req.request_id
        username   = $req.username
        action     = $req.action
        ad_group   = $groupName
        ou_path    = $ouPath
        status     = $status
    }
}

$auditLog | Format-Table -AutoSize
