$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'bootstrap-common.ps1')
$projectRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $projectRoot 'verification\source-manifest.json'
$manifest = [System.IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
$failures = 0
$count = 0
foreach ($entry in $manifest.files.PSObject.Properties) {
    $path = Join-Path $projectRoot $entry.Name
    $count++
    if (-not [System.IO.File]::Exists($path)) {
        Write-Host ('MISSING: ' + $entry.Name)
        $failures++
    } elseif ((Get-SourceSha256 -Path $path) -ne $entry.Value) {
        Write-Host ('CHANGED OR CORRUPT: ' + $entry.Name)
        $failures++
    }
}
if ($failures -gt 0) {
    throw ('Source verification failed: ' + $failures + ' files. Extract the complete source ZIP again, or review your intentional edits.')
}
Write-Host ('PASS: ' + $count + ' source/resource files match the delivery manifest.')
