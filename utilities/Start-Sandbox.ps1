<#
.SYNOPSIS
Starts one of the sandbox CLI examples in an idempotent, repeatable way.

.DESCRIPTION
Runs the selected sandbox command by using uv from the repository root,
and stores the last invocation so it can be restarted with Restart-Sandbox.ps1.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('basic', 'stream', 'system')]
    [string]$Command,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Prompt,

    [string]$Persona
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Import-Module (Join-Path $PSScriptRoot 'SandboxTools.psm1') -Force
Invoke-SandboxCommand -Command $Command -Prompt $Prompt -Persona $Persona -SaveLastRun
