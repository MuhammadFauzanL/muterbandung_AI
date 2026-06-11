param(
    [string]$TaskName = "CodexLocalBackup",
    [string]$StartTime = "00:00",
    [int]$EveryHours = 24,
    [string]$BackupScript = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($BackupScript)) {
    $BackupScript = Join-Path $PSScriptRoot "backup_codex_data.ps1"
}

if (-not (Test-Path -LiteralPath $BackupScript)) {
    throw "Backup script not found: $BackupScript"
}

$resolvedScript = (Resolve-Path -LiteralPath $BackupScript).Path
$actionArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$resolvedScript`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $actionArgs

if ($EveryHours -lt 1) {
    throw "EveryHours must be at least 1."
}

$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At $StartTime `
    -RepetitionInterval (New-TimeSpan -Hours $EveryHours) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Back up local Codex session and thread data daily." `
    -Force | Out-Null

Write-Host "Scheduled task installed:"
Write-Host "  Name: $TaskName"
Write-Host "  Start time: $StartTime"
Write-Host "  Interval: every $EveryHours hour(s)"
Write-Host "  Script: $resolvedScript"
Write-Host ""
Write-Host "Run manually anytime with:"
Write-Host "  powershell -ExecutionPolicy Bypass -File `"$resolvedScript`""
