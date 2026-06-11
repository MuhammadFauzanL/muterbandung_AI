param(
    [string]$CodexHome = "$env:USERPROFILE\.codex",
    [string]$BackupRoot = "",
    [switch]$IncludeAuth,
    [int]$KeepLatest = 30
)

$ErrorActionPreference = "Stop"

function New-DirectoryIfMissing {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
    }
}

function Copy-IfExists {
    param(
        [string]$Source,
        [string]$Destination
    )

    if (Test-Path -LiteralPath $Source) {
        $parent = Split-Path -Parent $Destination
        New-DirectoryIfMissing -Path $parent
        Copy-Item -LiteralPath $Source -Destination $Destination -Force -Recurse
        return $true
    }

    return $false
}

if (-not (Test-Path -LiteralPath $CodexHome)) {
    throw "Codex home not found: $CodexHome"
}

if ([string]::IsNullOrWhiteSpace($BackupRoot)) {
    $workspaceRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
    $BackupRoot = Join-Path $workspaceRoot "Codex_Backups"
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = Join-Path $BackupRoot "codex_backup_$timestamp"
$snapshotDir = Join-Path $backupDir "snapshot"
$zipPath = "$backupDir.zip"

New-DirectoryIfMissing -Path $snapshotDir

$copied = New-Object System.Collections.Generic.List[string]
$missing = New-Object System.Collections.Generic.List[string]

$paths = @(
    "sessions",
    "state_5.sqlite",
    "state_5.sqlite-wal",
    "state_5.sqlite-shm",
    "logs_2.sqlite",
    "logs_2.sqlite-wal",
    "logs_2.sqlite-shm",
    "goals_1.sqlite",
    "goals_1.sqlite-wal",
    "goals_1.sqlite-shm",
    "session_index.jsonl",
    "history.jsonl",
    "config.toml",
    "version.json",
    "installation_id"
)

if ($IncludeAuth) {
    $paths += "auth.json"
}

foreach ($relativePath in $paths) {
    $source = Join-Path $CodexHome $relativePath
    $destination = Join-Path $snapshotDir $relativePath
    if (Copy-IfExists -Source $source -Destination $destination) {
        $copied.Add($relativePath)
    } else {
        $missing.Add($relativePath)
    }
}

$manifest = [ordered]@{
    created_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
    codex_home = $CodexHome
    backup_dir = $backupDir
    zip_path = $zipPath
    include_auth = [bool]$IncludeAuth
    copied = $copied
    missing = $missing
    note = "auth.json is excluded by default because it may contain account credentials."
}

$manifestPath = Join-Path $backupDir "manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
Compress-Archive -LiteralPath $backupDir -DestinationPath $zipPath -Force

$existingZips = Get-ChildItem -LiteralPath $BackupRoot -Filter "codex_backup_*.zip" -File |
    Sort-Object LastWriteTime -Descending

if ($KeepLatest -gt 0 -and $existingZips.Count -gt $KeepLatest) {
    $existingZips | Select-Object -Skip $KeepLatest | Remove-Item -Force
}

Write-Host "Codex backup created:"
Write-Host "  Folder: $backupDir"
Write-Host "  Zip:    $zipPath"
Write-Host "  Copied: $($copied.Count) item(s)"
Write-Host "  Missing: $($missing.Count) item(s)"
if (-not $IncludeAuth) {
    Write-Host "  auth.json excluded. Use -IncludeAuth only if you intentionally want to back up credentials."
}
