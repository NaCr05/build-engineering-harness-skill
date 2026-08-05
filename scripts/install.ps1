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

$python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python -ErrorAction SilentlyContinue }
if (-not $python) { throw "Python 3 is required." }

$arguments = @($installer, "--repo", $Repository)
if ($Version) { $arguments += @("--version", $Version) }
if ($AssetDir) { $arguments += @("--asset-dir", $AssetDir) }
if ($CodexHome) { $arguments += @("--codex-home", $CodexHome) }
if ($DryRun) { $arguments += "--dry-run" }

& $python.Source @arguments
exit $LASTEXITCODE
