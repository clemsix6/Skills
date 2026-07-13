# Shared Skills Repository Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Factor the duplicated CLAUDE.md standards into a public `clemsix6/Skills` repo of `@`-importable fragments, kept fresh on every machine by a SessionStart hook, and wire TrueWallet, Hermenea and BluePods to consume them.

**Architecture:** A flat repo of 6 markdown fragments consumed via CLAUDE.md `@~/Skills/<fragment>.md` imports (deterministic, reaches subagents). Each git repo commits a `.claude/settings.json` SessionStart hook that clones/pulls `~/Skills`. Project CLAUDE.md files keep only project-specific content.

**Tech Stack:** Markdown, Claude Code `@` imports + hooks, git, `gh` CLI (authenticated as `clemsix6`), Notion MCP (TrueWallet tickets only).

## Global Constraints

- Spec: `docs/superpowers/specs/2026-07-13-shared-skills-repo-design.md` — the plan implements it exactly.
- Fragment content: English, generic only, zero project-specific or sensitive data (no Notion IDs, no server hosts, no staging URLs).
- Source line ranges below refer to the **pre-migration** files: `TW` = `/Users/clement/TrueWallet/CLAUDE.md`, `H` = `/Users/clement/Hermenea/CLAUDE.md`, `BP` = `/Users/clement/BluePods/.claude/CLAUDE.md`, `SK` = `/Users/clement/Skills/CLAUDE.md`. Read the source file and copy the range byte-faithfully; apply only the edits the step lists.
- Import lines are exactly `@~/Skills/<fragment>.md`, one per line, no bullet, no backticks.
- Every commit follows the `[+]/[-]/[&]/[!]` convention: title line without prefix, then prefixed body lines, **no footers of any kind**.
- Service repos: never push to `main` — branch `chore/shared-skills-standards`, push, open a PR.
- The standard import block for **Go repos** (5 lines):

```
@~/Skills/general.md
@~/Skills/go-style.md
@~/Skills/commit-convention.md
@~/Skills/git-workflow.md
@~/Skills/feature-pipeline.md
```

- The standard import block for **non-Go repos** is the same minus the `go-style` line (4 lines).
- The hook file, identical everywhere it is created, is `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "if [ -d \"$HOME/Skills/.git\" ]; then git -C \"$HOME/Skills\" pull --ff-only --quiet || true; else git clone --quiet https://github.com/clemsix6/Skills \"$HOME/Skills\" || true; fi"
          }
        ]
      }
    ]
  }
}
```

---

### Task 1: The six fragments

**Files:**
- Create: `/Users/clement/Skills/general.md`
- Create: `/Users/clement/Skills/go-style.md`
- Create: `/Users/clement/Skills/rust-style.md`
- Create: `/Users/clement/Skills/commit-convention.md`
- Create: `/Users/clement/Skills/git-workflow.md`
- Create: `/Users/clement/Skills/feature-pipeline.md`

**Interfaces:**
- Produces: the six fragment filenames — every later task's import lines and README refer to these exact names.

- [ ] **Step 1: Write `general.md`** — exact content:

````markdown
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
````

- [ ] **Step 2: Write `go-style.md`** — copy TW lines 5–107 verbatim (from `## Go Coding Standards` through the closing ``` of the Example Documentation Style block). Two edits:
  - TW line 71: `replace ../TrueWallet-Entities` → `replace ../some-local-module`.
  - Do NOT include TW lines 109–115 (`### CLAUDE.md Design`) — that section lives in `general.md`.

- [ ] **Step 3: Write `rust-style.md`** — copy SK from the line `## Rust Coding Standards` through the closing ``` of `### Example Documentation Style` verbatim. Do NOT include SK's `# CLAUDE.md` preamble (first 6 lines) nor its `### CLAUDE.md Design (CRUCIAL)` section.

- [ ] **Step 4: Write `commit-convention.md`** — copy TW lines 316–346 verbatim, with one edit: `All commits across TrueWallet repositories follow this format:` → `All commits follow this format:`.

- [ ] **Step 5: Write `git-workflow.md`** — copy BP lines 220–240 verbatim (`## Git Workflow` through the end of `### PR lifecycle`). BP holds the already-generic version (no Notion references). Then append this section at the end, exact text:

````markdown
### Working on the right code (CRUCIAL)

- Any analysis, investigation, or bug fix starts by checking the branch: be on
  the repo's default branch (`main`, `master`, or `dev` — whatever the repo
  uses) and up to date (`git pull`) before reading the code, unless the task
  explicitly targets another branch. Analyzing a stale or random checkout
  produces conclusions about code that no longer exists.
- When looking for a branch, `git fetch origin` first — the local clone does
  not have every remote branch, and branch listings without a fresh fetch lie.
````

- [ ] **Step 6: Write `feature-pipeline.md`** — merged content; exact text:

````markdown
## Development Workflow

This pipeline is for **adding a feature** — building something new. It wraps
review + autonomous-fix gates around the spec and the plan, and changes how the
plan is structured and executed.

**It applies to feature additions ONLY.** Debugging, bug fixes, refactors,
investigations, and ops do NOT follow it — no brainstorm, no spec, no worktree
ceremony. Fix bugs with systematic-debugging (reproduce → diagnose → fix →
verify), make small or contained changes directly, and use judgment. Reserve the
full pipeline below for genuinely new features.

The project CLAUDE.md may insert additional steps or override the task-workspace
pattern — check it before starting the pipeline.

### Pipeline (in order)

1. **Brainstorming** — superpowers `brainstorming` skill (standard).
2. **Spec** — write the spec (standard), in `docs/superpowers/specs/`.
3. **Spec review** — dispatch a subagent to review the spec: is it aligned with
   the brainstorm? Hunt for problems, gaps, and incoherences.
4. **Fix the spec** — apply the review feedback autonomously.
5. **Spec summary to the user** — only once the spec is corrected, send a
   bullet-point summary for the supervisor to validate. This is the single human
   checkpoint of the flow.
6. **Plan** — write the plan (see "Plan rules" below), in `docs/superpowers/plans/`.
7. **Plan + spec review** — dispatch a subagent to review the package; the spec
   matters but the focus is the plan: plan↔spec alignment, overall coherence,
   potential bugs/problems.
8. **Fix the plan** — apply the review feedback autonomously.
9. **Workspace + branch + PR** — as soon as the plan is clean (right after step
   8, before any implementation), create the isolated task workspace (see "Task
   workspace" below), branch, and open the draft PR with the superpowers docs
   inside. Keep the PR body up to date.
10. **Implementation** — chain it directly after the plan. Subagent-driven by
    default; inline only in the rare cases where it is recommended.

### Plan rules (differ from superpowers)

- **Single phase, mandatory** — at the end of the plan's first iteration,
  everything requested in the brainstorm is implemented. No "phase 2 later."
- **Batched tasks** — group the superpowers tasks into batches of ~1-5 so one
  subagent implements a whole batch (saves time and tokens).
- **1 task = 1 commit** — batching never merges commits; the task stays the unit
  of commit and audit.

### Per-batch rules

- **Each batch leaves the build green** — a batch carries its own wiring (the
  composition-root lines that construct the new code and make it reachable), so
  the feature is actually wired and the project's build and vet/lint commands
  pass with it reachable. Never defer all wiring to a final "wiring batch" —
  that leaves intermediate batches as dead, untestable code.
- At the end of a batch, if it is **critical**, run a code review of the batch
  and fix the feedback autonomously. Most of the time this is not needed.
- Then push all the batch's commits.

### Task workspace (autonomous — parallel-session isolation)

Several tasks can run in parallel sessions, but two sessions must never write
the same checkout. Sessions start from the repo root on an up-to-date `main`;
brainstorm, spec and plan all read the main checkout. Right before
implementation, create an isolated worktree so this session is the **sole
writer**, then do ALL implementation inside it. **Once the worktree exists,
never touch the main checkout for this task** — that single rule is what keeps
parallel sessions from colliding.

- **Create**: `git fetch origin`, then
  `git worktree add -b <type>/<task> .wt/<task> origin/main`.
  Branching from `origin/main` leaves the main checkout free for other sessions.
  (`.wt/` is gitignored.)
- **No CWD change** — absolute paths for edits; the `-C` flag for every command
  (`git -C .wt/<task> …`, `go -C .wt/<task> test ./...`).
- **Clean up** at merge: `git worktree remove .wt/<task>`. If the session ends
  before merge, leave it (`git worktree prune` reclaims stale ones later).
````

- [ ] **Step 7: Verify fragments against sources** — no rule lost, only the listed edits:

Run: `grep -c "^### .*CRUCIAL" /Users/clement/Skills/go-style.md` — Expected: `5` (KISS, Minimal Public API, Function Size, File Size, go.mod Hygiene).
Run: `grep -n "TrueWallet\|Hermenea\|BluePods\|Notion\|truewalletapp" /Users/clement/Skills/*.md` — Expected: no output (fragments are project-agnostic).

- [ ] **Step 8: Commit**

```bash
git -C /Users/clement/Skills add general.md go-style.md rust-style.md commit-convention.md git-workflow.md feature-pipeline.md
git -C /Users/clement/Skills commit -m "Shared standards fragments

[+] general.md — just conventions, delegation rule, CLAUDE.md design meta-rules
[+] go-style.md — Go coding standards (canonical text from TrueWallet)
[+] rust-style.md — Rust coding standards (moved from repo CLAUDE.md)
[+] commit-convention.md — [+]/[-]/[&]/[!] commit format
[+] git-workflow.md — branching and PR lifecycle
[+] feature-pipeline.md — custom superpowers pipeline with generic task workspace"
```

---

### Task 2: README and the repo's own CLAUDE.md

**Files:**
- Create: `/Users/clement/Skills/README.md`
- Modify: `/Users/clement/Skills/CLAUDE.md` (full replacement — Rust content now lives in `rust-style.md`)

**Interfaces:**
- Consumes: fragment filenames from Task 1.

- [ ] **Step 1: Write `README.md`** — exact content:

````markdown
# Skills

Shared engineering standards for my projects, consumed by Claude Code through
CLAUDE.md `@` imports. One clone per machine, at `~/Skills`, kept fresh
automatically — every agent on every machine follows the latest version.

## One-time setup (per machine)

```bash
git clone https://github.com/clemsix6/Skills ~/Skills
```

Wired projects also carry a `SessionStart` hook that clones this repo if absent
and pulls it otherwise, so after the first trusted session the clone maintains
itself. You will be asked to approve the hook the first time you trust a wired
project — that is expected.

## Wiring a project

1. Add the import lines at the top of the project's `CLAUDE.md`
   (create the file if the repo has none):

   ```
   @~/Skills/general.md
   @~/Skills/go-style.md
   @~/Skills/commit-convention.md
   @~/Skills/git-workflow.md
   @~/Skills/feature-pipeline.md
   ```

   Drop `go-style` for non-Go repos. For Rust code, import
   `@~/Skills/rust-style.md` — in a mixed repo, put that line in a
   `CLAUDE.md` inside the Rust subdirectory so it loads only when Rust files
   are touched.

2. Commit `.claude/settings.json` with the SessionStart hook:

   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "if [ -d \"$HOME/Skills/.git\" ]; then git -C \"$HOME/Skills\" pull --ff-only --quiet || true; else git clone --quiet https://github.com/clemsix6/Skills \"$HOME/Skills\" || true; fi"
             }
           ]
         }
       ]
     }
   }
   ```

## Fragments

| File | Contents |
|---|---|
| `general.md` | Cross-language defaults: command runner (just), CLAUDE.md design rules |
| `go-style.md` | Go coding standards |
| `rust-style.md` | Rust coding standards |
| `commit-convention.md` | Commit message format |
| `git-workflow.md` | Branching model and PR lifecycle |
| `feature-pipeline.md` | The feature-development pipeline (superpowers custom) |

## Rules of this repo

Fragments are generic: no project names, no credentials, no internal URLs or
IDs. Project-specific rules live in each project's own CLAUDE.md. Updates land
on `main` and propagate to every machine at the next session start.
````

- [ ] **Step 2: Replace `/Users/clement/Skills/CLAUDE.md`** — exact content:

````markdown
# CLAUDE.md

This repository holds shared engineering standards consumed by other projects
through CLAUDE.md `@` imports (see README.md).

## Editing rules

- All content in English.
- Fragments stay **project-agnostic**: no project names, no Notion IDs, no
  hosts, no URLs of internal systems, no credentials. Anything specific belongs
  in the consuming project's CLAUDE.md.
- One fragment = one theme. New cross-cutting defaults go to `general.md`;
  a new language gets its own `<lang>-style.md`.
- Every change lands on `main` and propagates to every machine at the next
  session start — treat each edit as immediately live everywhere.

@~/Skills/commit-convention.md
````

- [ ] **Step 3: Commit**

```bash
git -C /Users/clement/Skills add README.md CLAUDE.md
git -C /Users/clement/Skills commit -m "README and repo editing rules

[+] README — setup, wiring guide, fragments index
[&] CLAUDE.md — repo editing rules replace the Rust standards (moved to rust-style.md)"
```

---

### Task 3: Publish to GitHub

**Files:** none (remote operation).

- [ ] **Step 1: Create the public repo and push**

```bash
git -C /Users/clement/Skills branch -M main
gh repo create clemsix6/Skills --public --source /Users/clement/Skills --push
```

Expected: repo created, `main` pushed, origin remote set.

- [ ] **Step 2: Verify anonymous HTTPS clone works** (what collaborators' hooks will do)

```bash
git clone --quiet https://github.com/clemsix6/Skills /tmp/skills-clone-test && ls /tmp/skills-clone-test/*.md && rm -rf /tmp/skills-clone-test
```

Expected: the 6 fragments + README + CLAUDE.md listed.

---

### Task 4: TrueWallet parent directory

**Files:**
- Modify: `/Users/clement/TrueWallet/CLAUDE.md` (full rewrite)
- Create: `/Users/clement/TrueWallet/.claude/settings.json` (hook JSON from Global Constraints)

Not a git repository — no branch, no commit. Keep a safety copy first.

- [ ] **Step 1: Safety copy** — `cp /Users/clement/TrueWallet/CLAUDE.md /Users/clement/TrueWallet/CLAUDE.md.pre-migration` (deleted in Task 8).

- [ ] **Step 2: Rewrite `/Users/clement/TrueWallet/CLAUDE.md`** with this structure:

````markdown
# CLAUDE.md

This file provides global guidance to Claude Code when working across all TrueWallet repositories.

@~/Skills/general.md
@~/Skills/go-style.md
@~/Skills/commit-convention.md
@~/Skills/git-workflow.md
@~/Skills/feature-pipeline.md

## TrueWallet Pipeline Deltas

The shared pipeline (see Development Workflow above) applies with two additions:

### Extra step — Notion ticket (between steps 5 and 6)

[TW lines 139–146 verbatim, reworded opening: "Once the spec is validated, ensure the task's Notion ticket exists:" — keep the rest of the paragraph as is]

### Task workspace override — multi-repo

[TW lines 182–203 verbatim — the body only, the heading is above: the `.wt/<task>/` plain-dir workspace, one worktree per touched repo, `go.work` linking, no-CWD-change rule, cleanup]

## Git Workflow — TrueWallet specifics

[TW lines 219–264 verbatim — the range INCLUDES the `### Notion tickets` heading]

### PR lifecycle addition

The draft PR carries `Issue: <notion url>` at the top of the body, and the body
is filled from the repo's `.github/pull_request_template.md` — read it, complete
every section.

[TW lines 282–314 verbatim — the range INCLUDES the `### Deployment & Release (MEP)` heading]

## Tooling

[TW lines 350–351 verbatim: the gopls and Signoz MCP bullets]

## Server Access

[TW line 377 verbatim: the production-server ssh bullet]
````

- [ ] **Step 3: Write the hook** — create `/Users/clement/TrueWallet/.claude/settings.json` with the exact JSON from Global Constraints.

- [ ] **Step 4: Verify no rule lost**

Run: `grep -n "go.mod\|Justfile\|\[+\]\|squash" /Users/clement/TrueWallet/CLAUDE.md`
Expected: no hits for content now living in fragments (only import lines and TrueWallet-specific sections remain).

---

### Task 5: TrueWallet service repos (7)

**Files (per repo `R` in Backend, Entities, Processor, Dashboard, Frontend, Infra, LandingPage):**
- Modify: `/Users/clement/TrueWallet/R/CLAUDE.md` (prepend import block; LandingPage: create the file)
- Create: `/Users/clement/TrueWallet/R/.claude/settings.json`

**Interfaces:**
- Consumes: published repo from Task 3 (hooks reference it), import blocks from Global Constraints.
- Go repos (5-line block): Backend, Entities, Processor. Non-Go (4-line block): Dashboard, Frontend, Infra, LandingPage.

- [ ] **Step 1: Create the Notion ticket** — one ticket covers the whole migration, following the "Notion tickets" rules of the TrueWallet CLAUDE.md: search the Tasks Tracker for an existing ticket first; otherwise create one — title "Adopt shared Skills standards", body Objectif / Scope / Description (from the spec), `Priority` Medium, `Area` Infra, `Status` In progress, assignee resolved from git identity (`clement` / clement.dreiski@gmail.com) via the Notion users API. Keep the ticket URL for every PR body.

- [ ] **Step 2: Wire each repo.** For each repo `R`: prepend the language-appropriate import block (plus a blank line) at the top of `CLAUDE.md` — after the `# title` line when one exists; for LandingPage create `CLAUDE.md` containing only `# CLAUDE.md`, a blank line, and the 4-line block. Then write `.claude/settings.json` (exact hook JSON). Then:

```bash
git -C /Users/clement/TrueWallet/R checkout main && git -C /Users/clement/TrueWallet/R pull
git -C /Users/clement/TrueWallet/R checkout -b chore/shared-skills-standards
git -C /Users/clement/TrueWallet/R add CLAUDE.md .claude/settings.json
git -C /Users/clement/TrueWallet/R commit -m "Adopt shared Skills standards

[+] Shared standards imports from ~/Skills in CLAUDE.md
[+] SessionStart hook keeping ~/Skills fresh"
git -C /Users/clement/TrueWallet/R push -u origin chore/shared-skills-standards
```

- [ ] **Step 3: Open the PRs.** For each repo: read `.github/pull_request_template.md` if present, fill every section, put `Issue: <notion url>` as the first body line, then `gh pr create --draft --title "Adopt shared Skills standards" --body-file <filled body>`. Mark ready once CI is green. Upsert one page per PR in the Pull Requests data source per the TrueWallet Notion rules (relation to the ticket).

- [ ] **Step 4: Verify** — `gh pr list --repo TrueWalletApp/TrueWallet-R` shows the PR for each of the 7 repos.

---

### Task 6: Hermenea

**Files:**
- Modify: `/Users/clement/Hermenea/CLAUDE.md` (full rewrite, parent dir, not a git repo)
- Create: `/Users/clement/Hermenea/.claude/settings.json`
- Modify: `/Users/clement/Hermenea/Hermenea-Entities/CLAUDE.md` (prepend 5-line Go block)
- Create: `Hermenea-Agencies/CLAUDE.md`, `Hermenea-Backend/CLAUDE.md` (5-line Go block under a `# CLAUDE.md` title), `Hermenea-Frontend/CLAUDE.md` (4-line block)
- Create: `.claude/settings.json` in each of the 4 repos

- [ ] **Step 1: Safety copy** — `cp /Users/clement/Hermenea/CLAUDE.md /Users/clement/Hermenea/CLAUDE.md.pre-migration`.

- [ ] **Step 2: Rewrite `/Users/clement/Hermenea/CLAUDE.md`**:

````markdown
# CLAUDE.md

This file provides global guidance to Claude Code when working across all Hermenea repositories.

@~/Skills/general.md
@~/Skills/go-style.md
@~/Skills/commit-convention.md
@~/Skills/git-workflow.md
@~/Skills/feature-pipeline.md

## Repository Layout

[H lines 148–168 verbatim: Package Organization, Other Directories, Architecture Style]

## Database

[H lines 172–188 verbatim: Stack, Schema Ownership, When sqlc Doesn't Fit]

## Testing

[H lines 192–224 verbatim: Philosophy, Two speeds, Integration environment, The deliberate seam, LLM testing, Per-third-party strategy]

## Tooling

[H lines 270–271 verbatim: gopls]
````

- [ ] **Step 3: Hook + wiring of the 4 repos** — same mechanics as Task 5 Step 2 (branch `chore/shared-skills-standards`, same commit message, push, `gh pr create --draft`). No Notion step — Hermenea has no ticket requirement. Note: `git-workflow.md` and the worktree pattern are **new adoptions** for Hermenea, intended by the spec.

- [ ] **Step 4: Verify** — each repo has an open PR; `grep -c "@~/Skills" /Users/clement/Hermenea/*/CLAUDE.md` returns 5, 5, 5, 4 (Entities keeps its existing repo-specific content below the block).

---

### Task 7: BluePods

**Files:**
- Modify: `/Users/clement/BluePods/.claude/CLAUDE.md` (full rewrite)
- Create: `/Users/clement/BluePods/pods/CLAUDE.md`, `/Users/clement/BluePods/wasm-gas/CLAUDE.md`
- Create: `/Users/clement/BluePods/.claude/settings.json`

- [ ] **Step 1: Safety copy** — `cp /Users/clement/BluePods/.claude/CLAUDE.md /Users/clement/BluePods/.claude/CLAUDE.md.pre-migration`.

- [ ] **Step 2: Rewrite `/Users/clement/BluePods/.claude/CLAUDE.md`**:

````markdown
# BluePods Project

[BP lines 3–31 verbatim: Context Files, Documentation Conventions, Project Layout]

@~/Skills/general.md
@~/Skills/go-style.md
@~/Skills/commit-convention.md
@~/Skills/git-workflow.md
@~/Skills/feature-pipeline.md

## BluePods Pipeline Deltas

- When a batch touches `pods/` or `wasm-gas/`, their builds and tests must pass
  too before the batch is considered green.
- Heavy batches (consensus, multi-file, hours of work) are implemented
  task-by-task by successive fresh subagents — a single agent must never carry
  hours of dense work in one context. Implementers commit as soon as unit tests
  pass; slow integration sims run AFTER the commit (a failure becomes a
  follow-up fix commit).
````

- [ ] **Step 3: Create the Rust subdirectory CLAUDE.md files** — both `pods/CLAUDE.md` and `wasm-gas/CLAUDE.md` contain exactly:

```
@~/Skills/rust-style.md
```

- [ ] **Step 4: Hook, branch, commit, PR** — write `.claude/settings.json`; then branch `chore/shared-skills-standards`, commit:

```
Adopt shared Skills standards

[+] Shared standards imports from ~/Skills in .claude/CLAUDE.md
[+] pods/ and wasm-gas/ CLAUDE.md importing the Rust style on demand
[+] SessionStart hook keeping ~/Skills fresh
[-] Duplicated Go standards, commit convention, git workflow and pipeline (now fragments)
```

push, `gh pr create --draft` on `clemsix6/BluePods`.

---

### Task 8: Validation (spec "Validation" section)

- [ ] **Step 1: Coverage diff** — for each `.pre-migration` copy, verify every section is either in a fragment or in the rewritten file: `grep "^##" CLAUDE.md.pre-migration` and check each heading against (fragments ∪ new file). No heading may be unaccounted for.
- [ ] **Step 2: Fresh-session checks** (manual, with the user): in TrueWallet, a new session states the commit convention and the 25-line function limit without opening files; same in a `.wt/` worktree; a BluePods Go session does NOT know the Rust rules until a `pods/` file is touched.
- [ ] **Step 3: Offline check** — disable network, start a session in a wired project: the hook exits silently, the session works on the local clone.
- [ ] **Step 4: Cleanup** — delete the three `.pre-migration` copies; commit any spec/plan corrections discovered; report results to the user.
