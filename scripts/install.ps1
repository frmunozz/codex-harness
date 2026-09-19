[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RemainingArgs
)

$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
$pythonArgs = @()
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
    $pythonArgs = @("-3")
}
if (-not $python) {
    throw "Python 3 is required. Install it, then rerun this script."
}

& $python.Source @pythonArgs (Join-Path $PSScriptRoot "codex_harness.py") install @RemainingArgs
exit $LASTEXITCODE
