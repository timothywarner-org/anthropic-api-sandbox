<#
.SYNOPSIS
Runs the system-prompt sandbox example and stores it as the last run.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Persona,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Prompt
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'Start-Sandbox.ps1') -Command system -Persona $Persona -Prompt $Prompt
