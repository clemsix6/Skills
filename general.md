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

### Comments Must Not Rot (CRUCIAL)

A comment is written once and read for years while the code under it keeps
moving. Anything a comment states that the code can change on its own becomes a
lie eventually — and nothing catches it: no compiler, no test, no reviewer flags
a comment that quietly stopped being true. So a comment must only say things
that survive the next edit.

- **No hardcoded values.** Never restate a literal the code already holds —
  limits, timeouts, sizes, ports, counts, prices, version numbers, field lists.
  Say what the value is *for* and let the reader look at it: "retries transient
  failures with exponential backoff", not "retries 5 times, 2s apart". The next
  person who tunes the number will not think to update the sentence.
- **No temporal statements.** Nothing whose truth depends on when it is read:
  "new", "current", "for now", "temporary", "recently added", "will be removed
  next quarter", dates, sprint or release numbers, "replaces the old X". Time
  invalidates these with nobody touching the file — git history already records
  when and why something changed.
- **Describe intent and invariants, not state.** Why the code exists and what
  must hold are stable; what the value happens to be today and what the codebase
  looked like when it was written are not.
- **Exception**: a constraint that lives *outside* the codebase — a third-party
  API limit, a protocol constant, a spec requirement — may be cited when it is
  the reason the code is shaped that way, and then it is named with its source
  so a reader can re-check it.
- TODO comments stay allowed: they describe the work left to do, never a date or
  a release it is promised for.

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
