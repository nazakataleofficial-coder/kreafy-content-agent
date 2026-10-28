param(
    [Parameter(Mandatory=$true)][string]$PythonExe
)
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$PythonExe = (Resolve-Path $PythonExe).Path
if (-not (Test-Path (Join-Path $RepoRoot 'studio-private/delivery.sqlite3'))) {
    throw 'Persistent publication journal missing. Configure and verify publication first.'
}
# Only call this installer on the publication machine. Never send passwords.
$TaskName = 'Kreafy-Verified-Render-Cleanup'
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    throw 'Cleanup task already exists; inspect it before making changes.'
}
Push-Location $RepoRoot
try {
    & $PythonExe -m studio.cleanup
    if ($LASTEXITCODE -ne 0) { throw 'Dry-run failed; task was not installed.' }
} finally { Pop-Location }
$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument '-m studio.cleanup --apply' -WorkingDirectory $RepoRoot
$Trigger = New-ScheduledTaskTrigger -Daily -At '12:00'
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
$Principal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description 'Remove registered local renders 72 hours after all four verified publications; retain sources and receipts.'
Write-Output 'Cleanup registered at noon in this PC timezone. PC must be on and this Windows user logged in.'
