[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Low')]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$manifestPath = Join-Path $projectRoot 'verification\cleanup-paths.json'
$sourceManifest = Join-Path $projectRoot 'verification\source-manifest.json'
foreach ($required in @('settings.gradle', 'build.gradle', 'flora\src\main\java\dev\chromus\flora\ChromusFlora.java')) {
    if (-not [System.IO.File]::Exists((Join-Path $projectRoot $required))) {
        throw ('Incomplete project root: ' + $required)
    }
}
& (Join-Path $PSScriptRoot 'verify-source.ps1')
$rules = [System.IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
$active = ([System.IO.File]::ReadAllText($sourceManifest) | ConvertFrom-Json).files.PSObject.Properties.Name
$rootPrefix = $projectRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
$candidates = @()
foreach ($relative in $rules.paths) {
    if ([System.IO.Path]::IsPathRooted($relative) -or $relative -match '(^|[\\/])\.\.([\\/]|$)' -or $relative -match '[:*?]') {
        throw ('Invalid cleanup path: ' + $relative)
    }
    $normalized = $relative.Replace('\', '/').TrimEnd('/')
    $first = ($normalized -split '/')[0]
    if ($first -in @('.git', '.github', 'run', 'saves', 'mods', 'config', '.gradle', '.gradle-bootstrap', '.source-backups')) {
        throw ('Protected cleanup path: ' + $relative)
    }
    foreach ($name in $active) {
        if ($name -eq $normalized -or $name.StartsWith($normalized + '/', [System.StringComparison]::OrdinalIgnoreCase)) {
            throw ('Cleanup would remove an active file: ' + $name)
        }
    }
    $path = [System.IO.Path]::GetFullPath((Join-Path $projectRoot $relative))
    if (-not $path.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw ('Cleanup path escaped project root: ' + $relative)
    }
    if (Test-Path -LiteralPath $path) {
        $ancestor = $path
        while ($ancestor -and $ancestor.Length -ge $projectRoot.Length) {
            $item = Get-Item -LiteralPath $ancestor -Force
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw ('Link or junction requires manual review: ' + $ancestor)
            }
            $ancestor = Split-Path -Parent $ancestor
        }
        $candidates += [PSCustomObject]@{ Relative = $relative; FullPath = $path }
    }
}
if ($candidates.Count -eq 0) {
    Write-Host 'Project is already clean. No files moved.'
    return
}
if (-not $WhatIfPreference) {
    Push-Location $projectRoot
    try {
        & (Join-Path $projectRoot 'gradlew.bat') --stop
        if ($LASTEXITCODE -ne 0) { throw 'Could not stop Gradle. Close the IDE and running builds.' }
    } finally { Pop-Location }
}
$backupName = (Split-Path -Leaf $projectRoot) + '-backup-0.1.4-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$backupRoot = Join-Path (Split-Path -Parent $projectRoot) $backupName
foreach ($entry in $candidates) {
    $destination = Join-Path $backupRoot $entry.Relative
    if ($PSCmdlet.ShouldProcess($entry.FullPath, ('Move to backup: ' + $destination))) {
        [System.IO.Directory]::CreateDirectory((Split-Path -Parent $destination)) | Out-Null
        Move-Item -LiteralPath $entry.FullPath -Destination $destination -ErrorAction Stop
        Write-Host ('Removed from project, preserved in backup: ' + $entry.Relative)
    }
}
if (-not $WhatIfPreference) {
    & (Join-Path $PSScriptRoot 'verify-source.ps1')
    Write-Host ('Cleanup complete. Backup: ' + $backupRoot)
    Write-Host 'Next: .\gradlew.bat build --no-daemon --warning-mode=fail'
}
