Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
    [CmdletBinding()]
    param()

    return (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}

function Get-UvCommand {
    [CmdletBinding()]
    param()

    $uv = Get-Command -Name uv -ErrorAction SilentlyContinue
    if (-not $uv) {
        throw 'uv is not installed or not on PATH. Install uv from https://docs.astral.sh/uv/.'
    }

    return $uv.Source
}

function Get-StatePath {
    [CmdletBinding()]
    param()

    return (Join-Path $PSScriptRoot '.state\last-run.json')
}

function Save-LastRun {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('basic', 'stream', 'system')]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [string]$Prompt,

        [string]$Persona
    )

    $statePath = Get-StatePath
    $stateDir = Split-Path -Path $statePath -Parent
    if (-not (Test-Path -LiteralPath $stateDir)) {
        New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
    }

    $payload = [pscustomobject]@{
        command   = $Command
        prompt    = $Prompt
        persona   = $Persona
        timestamp = (Get-Date).ToString('o')
    }

    $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding utf8
}

function Invoke-SandboxCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('basic', 'stream', 'system')]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$Prompt,

        [string]$Persona,

        [switch]$SaveLastRun
    )

    if ($Command -eq 'system' -and [string]::IsNullOrWhiteSpace($Persona)) {
        throw 'The system command requires -Persona.'
    }

    if ($SaveLastRun) {
        Save-LastRun -Command $Command -Prompt $Prompt -Persona $Persona
    }

    $repoRoot = Get-RepoRoot
    $uv = Get-UvCommand

    $args = @('run', 'sandbox', $Command)
    if ($Command -eq 'system') {
        $args += @('--persona', $Persona)
    }
    $args += $Prompt

    Push-Location $repoRoot
    try {
        & $uv @args
        if ($LASTEXITCODE -ne 0) {
            throw "sandbox exited with code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }
}

function Restart-SandboxLast {
    [CmdletBinding()]
    param()

    $statePath = Get-StatePath
    if (-not (Test-Path -LiteralPath $statePath)) {
        throw "No previous run state found at $statePath. Run Start-Sandbox.ps1 first."
    }

    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    if (-not $state.command -or -not $state.prompt) {
        throw "State file is invalid: $statePath"
    }

    Invoke-SandboxCommand -Command $state.command -Prompt $state.prompt -Persona $state.persona -SaveLastRun
}

Export-ModuleMember -Function Invoke-SandboxCommand, Restart-SandboxLast
