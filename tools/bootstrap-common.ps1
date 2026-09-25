function Get-SourceSha256 {
    param([Parameter(Mandatory = $true)][string]$Path)

    $stream = [System.IO.File]::OpenRead($Path)
    $algorithm = $null
    try {
        $algorithm = [System.Security.Cryptography.SHA256]::Create()
        return [System.BitConverter]::ToString($algorithm.ComputeHash($stream)).Replace('-', '').ToLowerInvariant()
    } finally {
        if ($null -ne $algorithm) {
            $algorithm.Dispose()
        }
        $stream.Dispose()
    }
}

function Expand-VerifiedGradle {
    param(
        [Parameter(Mandatory = $true)][string]$Archive,
        [Parameter(Mandatory = $true)][string]$CacheRoot,
        [Parameter(Mandatory = $true)][string]$Version,
        [Parameter(Mandatory = $true)][string]$ExpectedHash
    )

    if ((Get-SourceSha256 -Path $Archive) -ne $ExpectedHash) {
        throw 'Gradle archive failed SHA-256 verification.'
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $staging = Join-Path $CacheRoot ('extract-' + [System.Guid]::NewGuid().ToString('N'))
    $destination = Join-Path $CacheRoot ('gradle-' + $Version)
    try {
        [System.IO.Compression.ZipFile]::ExtractToDirectory($Archive, $staging)
        $extracted = Join-Path $staging ('gradle-' + $Version)
        if (-not [System.IO.File]::Exists((Join-Path $extracted 'bin\gradle.bat'))) {
            throw 'The verified distribution does not contain the Gradle launcher.'
        }
        [System.IO.File]::WriteAllText((Join-Path $extracted '.verified-sha256'), $ExpectedHash)
        if (Test-Path -LiteralPath $destination) {
            Remove-Item -LiteralPath $destination -Recurse -Force
        }
        [System.IO.Directory]::Move($extracted, $destination)
    } finally {
        if (Test-Path -LiteralPath $staging) {
            Remove-Item -LiteralPath $staging -Recurse -Force
        }
    }
}
