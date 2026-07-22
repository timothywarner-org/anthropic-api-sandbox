<#
.SYNOPSIS
Re-runs the last sandbox invocation with no additional input.

.DESCRIPTION
Reads utilities/.state/last-run.json and replays the same sandbox command.
Useful for no-brainer retries during demos.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Import-Module (Join-Path $PSScriptRoot 'SandboxTools.psm1') -Force
Restart-SandboxLast
