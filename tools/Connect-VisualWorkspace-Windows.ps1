# Connect-VisualWorkspace-Windows.ps1
# Manual Windows clone/pull. Does not run project code.
[CmdletBinding()]
param(
    [ValidateSet('Sync', 'Clone', 'Pull')]
    [string]$Mode = 'Sync',
    [ValidatePattern('^[A-Za-z0-9._/-]+$')]
    [string])

$ErrorActionPreference = 'Stop'
$Root = 'C:\Users\alexa\Repos'
$Target = Join-Path $Root 'visual-workspace'
$Remote = 'https://github.com/AlexPastukhh/visual-workspace.git'

if (-not (Get-Command git.exe -ErrorAction SilentlyContinue)) {
    throw 'Git for Windows is not installed or git.exe is not in PATH.'
}
if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
    throw "Repositories directory does not exist: $Root"
}

if (-not (Test-Path -LiteralPath $Target)) {
    if ($Mode -eq 'Pull') {
        throw "Cannot pull: folder does not exist: $Target"
    }
    Write-Host "Cloning private repository into $Target"
    & git.exe clone --origin origin --branch $Branch --single-branch $Remote $Target
    if ($LASTEXITCODE -ne 0) {
        throw 'Clone failed. Check Git for Windows GitHub authentication.'
    }
    Write-Host "Clone complete: $Target"
    Write-Host 'Docker files appear here only after they have been pushed to GitHub.'
    return
}

if ($Mode -eq 'Clone') {
    throw "Target already exists; refusing to overwrite: $Target"
}
if (-not (Test-Path -LiteralPath (Join-Path $Target '.git'))) {
    throw "Target exists but is not a Git clone; refusing to modify: $Target"
}

$OriginUrl = (& git.exe -C $Target remote get-url origin)
if ($LASTEXITCODE -ne 0) { throw 'Cannot read origin.' }
if (($OriginUrl -join '').Trim() -ine $Remote) {
    throw 'Origin is not the expected repository; refusing to pull.'
}
$CurrentBranch = (& git.exe -C $Target branch --show-current)
if ($LASTEXITCODE -ne 0 -or ($CurrentBranch -join '').Trim() -ne $Branch) {
    throw "Current branch is not $Branch; refusing to pull."
}
$Changes = @(& git.exe -C $Target status --porcelain=v1)
if ($LASTEXITCODE -ne 0) { throw 'Cannot read Git status.' }
if (@($Changes | Where-Object { $_ }).Count -gt 0) {
    throw 'Local changes or untracked files exist; refusing to pull.'
}

Write-Host "Fast-forward pull from origin/$Branch into $Target"
& git.exe -C $Target pull --ff-only origin $Branch
if ($LASTEXITCODE -ne 0) {
    throw 'Pull failed. No reset, force, stash or deletion was attempted.'
}
Write-Host "Updated: $Target"
Write-Host 'Pulled project files are untrusted until reviewed; this script does not execute them.'
