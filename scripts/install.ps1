[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RemainingArgs
)

$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    throw "Python 3 is required. Install it, then rerun this script."
}

& $python.Source (Join-Path $PSScriptRoot "codex_harness.py") install @RemainingArgs
exit $LASTEXITCODE
