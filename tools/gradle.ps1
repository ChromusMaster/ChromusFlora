param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GradleArguments)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
. (Join-Path $PSScriptRoot 'bootstrap-common.ps1')
$projectRoot = Split-Path -Parent $PSScriptRoot
$gradleVersion = '9.5.1'
$expectedHash = 'bafc141b619ad6350fd975fc903156dd5c151998cc8b058e8c1044ab5f7b031f'
$cacheRoot = Join-Path $projectRoot '.gradle-bootstrap'
$gradleRoot = Join-Path $cacheRoot ('gradle-' + $gradleVersion)
$launcher = Join-Path $gradleRoot 'bin\gradle.bat'
$marker = Join-Path $gradleRoot '.verified-sha256'

if ($env:JAVA_HOME) {
    $javaExecutable = Join-Path $env:JAVA_HOME 'bin\java.exe'
} else {
    $javaExecutable = (Get-Command java.exe -ErrorAction Stop).Source
}
if (-not (Test-Path -LiteralPath $javaExecutable)) {
    throw 'Install JDK 25 and set JAVA_HOME to its installation folder.'
}
$previousErrorPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$javaInformation = & $javaExecutable -XshowSettings:properties -version 2>&1 | Out-String
$javaExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorPreference
if ($javaExitCode -ne 0 -or $javaInformation -notmatch 'java\.specification\.version\s*=\s*25\s') {
    throw 'This project requires JDK 25. Check JAVA_HOME and java -version.'
}

[System.IO.Directory]::CreateDirectory($cacheRoot) | Out-Null
$lockPath = Join-Path $cacheRoot 'bootstrap.lock'
try {
    $bootstrapLock = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
} catch {
    throw 'Another Gradle bootstrap may be running, or the cache is not writable. Close the other bootstrap and try again.'
}
try {
    $ready = [System.IO.File]::Exists($launcher) -and [System.IO.File]::Exists($marker)
    if ($ready) {
        $ready = [System.IO.File]::ReadAllText($marker).Trim() -eq $expectedHash
    }
    if (-not $ready) {
        $archive = Join-Path $cacheRoot ('gradle-' + $gradleVersion + '-bin.zip')
        $temporaryArchive = $archive + '.part'
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        try {
            if ([System.IO.File]::Exists($archive) -and (Get-SourceSha256 -Path $archive) -ne $expectedHash) {
                Remove-Item -LiteralPath $archive -Force
            }
            if (-not [System.IO.File]::Exists($archive)) {
                Write-Host ('Downloading Gradle ' + $gradleVersion + '...')
                Invoke-WebRequest -Uri ('https://services.gradle.org/distributions/gradle-' + $gradleVersion + '-bin.zip') -OutFile $temporaryArchive -UseBasicParsing
                if ((Get-SourceSha256 -Path $temporaryArchive) -ne $expectedHash) {
                    throw 'Gradle download failed SHA-256 verification. No downloaded code was executed. Run the command again.'
                }
                [System.IO.File]::Move($temporaryArchive, $archive)
            }
            Expand-VerifiedGradle -Archive $archive -CacheRoot $cacheRoot -Version $gradleVersion -ExpectedHash $expectedHash
        } finally {
            if (Test-Path -LiteralPath $temporaryArchive) {
                Remove-Item -LiteralPath $temporaryArchive -Force
            }
        }
    }
} finally {
    $bootstrapLock.Dispose()
}

if (-not $GradleArguments -or $GradleArguments.Count -eq 0) {
    $GradleArguments = @('build', '--warning-mode=fail')
}
Push-Location $projectRoot
try {
    & $launcher @GradleArguments
    $result = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $result
