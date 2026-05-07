Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Checking required files..."
$required = @(
  "README.md",
  ".env.example",
  "requirements.txt",
  "Dockerfile",
  "docker-compose.yml",
  "docs/setup.md",
  "docs/troubleshooting.md",
  "docs/utm-links.md",
  "app/main.py",
  "scripts/scan-secrets.js",
  "LICENSE",
  ".gitignore"
)

foreach ($path in $required) {
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Missing required file: $path"
  }
}

Write-Host "Checking Python syntax if a real Python interpreter is available..."
$pythonCommand = $null
foreach ($candidate in @("python", "py")) {
  $command = Get-Command $candidate -ErrorAction SilentlyContinue
  if (-not $command) {
    continue
  }
  if ($command.Source -like "*WindowsApps*") {
    continue
  }

  $versionOutput = & $candidate --version 2>&1
  if ($LASTEXITCODE -eq 0 -and ($versionOutput -join "`n") -notmatch "Microsoft Store") {
    $pythonCommand = $candidate
    break
  }
}

if ($pythonCommand) {
  & $pythonCommand -m py_compile app/main.py
} else {
  Write-Host "Real Python interpreter not found; skipped py_compile."
}

Write-Host "Checking secret scan if Node is available..."
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
  node scripts/scan-secrets.js
} else {
  Write-Host "Node not found; skipped scan-secrets.js."
}

Write-Host "All available checks passed."
