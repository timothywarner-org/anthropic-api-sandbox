<#
.SYNOPSIS
Runs the basic sandbox example and stores it as the last run.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Prompt
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'Start-Sandbox.ps1') -Command basic -Prompt $Prompt
