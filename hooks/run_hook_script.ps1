param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$ScriptName,
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$ExtraArgs
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $scriptDir $ScriptName

function Resolve-PythonRunner {
  $candidates = @('python', 'python3')

  foreach ($name in $candidates) {
    $commands = Get-Command $name -All -ErrorAction SilentlyContinue
    foreach ($command in $commands) {
      if ($command.CommandType -ne 'Application') {
        continue
      }

      $source = $command.Source
      if ([string]::IsNullOrWhiteSpace($source)) {
        continue
      }

      if ($source -match 'WindowsApps[\\/].*python(3)?\.exe$') {
        continue
      }

      if (Test-Path -LiteralPath $source) {
        return @{ Kind = 'Executable'; Value = $source }
      }
    }
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($null -ne $py -and $py.CommandType -eq 'Application' -and (Test-Path -LiteralPath $py.Source)) {
    return @{ Kind = 'Launcher'; Value = $py.Source }
  }

  return $null
}

$runner = Resolve-PythonRunner
if ($null -ne $runner) {
  if ($runner.Kind -eq 'Executable') {
    & $runner.Value $target @ExtraArgs
    exit $LASTEXITCODE
  }

  & $runner.Value -3 $target @ExtraArgs
  exit $LASTEXITCODE
}

Write-Error 'Hook dispatcher needs python3 or python in PATH.'
exit 1
