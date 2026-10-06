$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'bootstrap-common.ps1')
$projectRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $projectRoot 'verification\source-manifest.json'
$manifest = [System.IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
$failures = 0
$count = 0
$localConfigurations = @('.vscode/settings.json', 'README.md')
$optionalDocumentation = @(
    'APLICAR_0.1.4.md',
    'docs/DESEMPENHO_0.1.2.md',
    'docs/DOOR_TRAPDOOR_TEST_INDEX.md',
    'docs/REVISAO_0.1.1.md',
    'docs/REVISAO_0.1.2.md',
    'docs/REVISAO_0.1.3.md',
    'docs/REVISAO_0.1.4.md'
)
$localCount = 0
foreach ($entry in $manifest.files.PSObject.Properties) {
    if ($localConfigurations -contains $entry.Name) {
        $localCount++
        Write-Host ('LOCAL CONFIG (editable, not integrity-checked): ' + $entry.Name)
        continue
    }
    if ($optionalDocumentation -contains $entry.Name) {
        Write-Host ('OPTIONAL DOCUMENTATION (editable or removable): ' + $entry.Name)
        continue
    }
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
if ($localCount -gt 0) {
    Write-Host ('INFO: ' + $localCount + ' README/editor files may differ from the shipped defaults.')
}
