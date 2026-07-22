---
name: PowerShell and O'Reilly Teaching Rules
description: Guidance for PowerShell-family files and teaching-focused examples in this repo
applyTo: "**/*.{ps1,psm1,psd1,ps1xml,pssc,psrc,cdxml}"
---

<!-- Tip: Use /create-instructions in chat to generate content with agent assistance -->

# Project context

- This repository is a teaching sandbox for the Anthropic API CLI workflow.
- Prefer practical examples that are short, runnable, and production-minded.
- Use PowerShell 7 syntax for shell automation unless the task explicitly requires another shell.

# PowerShell coding guidelines

- Favor idempotent scripts. Re-running a command should not produce harmful side effects.
- Use parameter validation (`[Parameter()]`, `ValidateSet`, `ValidatePattern`) for script and function inputs.
- Fail loudly and helpfully: set strict mode where appropriate, use `try/catch`, and return actionable errors.
- Use advanced functions for reusable logic (`[CmdletBinding()]`) and include comment-based help.
- Keep output predictable for demos: emit structured objects first, then format for display at the edge.
- Never hardcode secrets. Read from environment variables or secure stores.

# Documentation and grounding rules

- Ground technical claims in first-party docs when possible.
- For Microsoft platform guidance, use Microsoft Learn MCP-backed documentation discovery before making assertions.
- For SDK and protocol behavior, prefer current MCP-backed docs and cite assumptions when behavior is uncertain.

# Teaching notes: YAML frontmatter examples

Use these as current reference examples in class.

```yaml
# .instructions.md frontmatter
---
name: Python Standards
description: Coding conventions for Python files
applyTo: "**/*.py"
---
```

```yaml
# .prompt.md frontmatter (additional properties)
---
name: review-api
description: Review an API surface for breaking changes
argument-hint: "Paste endpoint signatures or schema"
agent: agent
model: GPT-5.3-Codex
tools:
  - github
  - microsoft_docs
---
```

# Review checklist for AI-generated PowerShell

- Inputs validated and defaults are explicit.
- Errors are caught and surfaced with context.
- Secrets are externalized.
- Output objects are testable.
- Example commands are copy-paste ready for learners.
