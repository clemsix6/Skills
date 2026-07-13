## General Defaults

Cross-project defaults that apply to every repository, regardless of language.

### Command Runner (CRUCIAL)

- Use **just** (`Justfile`, github.com/casey/just) for command running — never a
  `Makefile`, never Task/`Taskfile.yml`.
- **KISS, minimal API** — define only the recipes actually needed. The same
  minimal-public-API rule that governs the code governs the Justfile. No recipe
  "just in case."
- **Quiet, sober output** — `set quiet` at the top; no banners, no emojis. One
  doc-comment (`#`) per recipe so `just --list` reads as the repo's command index.
- **Shebang recipes** (`#!/usr/bin/env bash`, `set -euo pipefail`) for any
  multi-line shell logic — never backslash-chained one-liners.
- **Go repos set `GOWORK` conditionally** — use the parent `go.work` when it
  exists (worktree/multi-module dev), fall back to `off` when absent (CI and
  Docker check out the repo alone). A bare `export GOWORK := … / "go.work"`
  breaks `go` in CI/Docker.

### Delegation rule (CRUCIAL)

CI and Docker delegate to `just` **only when the command is not already
centralized elsewhere.** If `package.json` (or another file) is already the
single source of truth, the Justfile is a local convenience alias and CI/Docker
keep calling the existing source. Do not stack `just` on top of an existing
centralization just to add a binary.

### CLAUDE.md Design (CRUCIAL)

- CLAUDE.md files describe the **why** and **principles** — not the exact file
  tree or package/crate list
- Do NOT put architecture diagrams with exact directory listings — they become
  stale after every refactor
- Describe architecture style and rules, not the current structure
- The code is its own documentation for structure — CLAUDE.md captures what is
  NOT visible in the code
- A good CLAUDE.md should rarely need updating; if it changes every commit,
  it's too specific
