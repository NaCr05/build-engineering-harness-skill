[CmdletBinding()]
param(
    [string]$Version,
    [string]$Repository = "NaCr05/build-engineering-harness-skill",
    [string]$AssetDir,
    [string]$CodexHome,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$installer = Join-Path $PSScriptRoot "install_skill.py"
if (-not (Test-Path -LiteralPath $installer -PathType Leaf)) {
    throw "Missing sibling installer: $installer"
}

$python = $null
foreach ($name in @("python", "python3")) {
    $candidate = Get-Command $name -ErrorAction SilentlyContinue
    if (-not $candidate) { continue }
    & $candidate.Source --version *> $null
    if ($LASTEXITCODE -eq 0) {
        $python = $candidate
        break
    }
}
if (-not $python) { throw "A working Python 3 interpreter is required." }

$arguments = @($installer, "--repo", $Repository)
if ($Version) { $arguments += @("--version", $Version) }
if ($AssetDir) { $arguments += @("--asset-dir", $AssetDir) }
if ($CodexHome) { $arguments += @("--codex-home", $CodexHome) }
if ($DryRun) { $arguments += "--dry-run" }

& $python.Source @arguments
exit $LASTEXITCODE
