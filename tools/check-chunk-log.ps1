param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath
)

$ErrorActionPreference = 'Stop'
$resolved = (Resolve-Path -LiteralPath $LogPath).Path
$reader = [System.IO.File]::OpenText($resolved)
$unsafeReads = 0
$unsafeWrites = 0
$featureCycles = 0
$vegetationRepairApplied = $false
$chunkFailures = 0
$guardApplied = $false
$unreviewed = $false
$samples = New-Object 'System.Collections.Generic.List[string]'
try {
    while ($null -ne ($line = $reader.ReadLine())) {
        if ($line.Contains('Applied Naturalist 2.0.6 hippo worldgen read guard (Chromus Flora hotfix 3)')) {
            $guardApplied = $true
        }
        if ($line.Contains('hippo worldgen read guard is not enabled')) { $unreviewed = $true }
        if ($line.Contains('Applied vegetation order compatibility (Chromus Flora hotfix 4)')) {
            $vegetationRepairApplied = $true
        }
        if ($line.Contains('Detected setBlock in a far chunk')) {
            $unsafeWrites++
            if ($samples.Count -lt 5) { $samples.Add($line) }
        }
        if ($line -match 'Feature order cycle|Vanilla feature indexer failed|Dropping cycle-forming edge') {
            $featureCycles++
            if ($samples.Count -lt 5) { $samples.Add($line) }
        }
        if ($line.Contains('Detected unsafe terrain read during worldgen')) {
            $unsafeReads++
            if ($samples.Count -lt 5) { $samples.Add($line) }
        }
        if ($line -match 'Exception (accessing|generating new) chunk|Failed to (read|load|save) chunk|Couldn.t load chunk|Error (loading|reading|saving) chunk') {
            $chunkFailures++
            if ($samples.Count -lt 5) { $samples.Add($line) }
        }
    }
} finally {
    $reader.Dispose()
}

Write-Host ('Log: ' + $resolved)
Write-Host ('Naturalist hotfix 3 applied: ' + $guardApplied)
Write-Host ('Unreviewed Naturalist version: ' + $unreviewed)
Write-Host ('Unsafe terrain reads: ' + $unsafeReads)
Write-Host ('Unsafe far-chunk writes: ' + $unsafeWrites)
Write-Host ('Feature-order cycle/recovery events: ' + $featureCycles)
Write-Host ('Vegetation order hotfix 4 applied: ' + $vegetationRepairApplied)
Write-Host ('Chunk access/generation/storage failures: ' + $chunkFailures)
foreach ($sample in $samples) { Write-Host $sample }
if ($unsafeReads -gt 0 -or $unsafeWrites -gt 0 -or $featureCycles -gt 0 -or $chunkFailures -gt 0) {
    Write-Host 'FAIL: chunk errors remain in this log. Send the complete log for analysis.'
    exit 1
}
if (-not $guardApplied -or $unreviewed) {
    Write-Host 'INCONCLUSIVE: no matching chunk errors, but hotfix activation was not confirmed in this log.'
    exit 2
}
Write-Host 'PASS: hotfix activation confirmed; no matching chunk errors in this session.'
Write-Host 'This checks the supplied log only; it does not prove all possible modpack combinations are error-free.'
