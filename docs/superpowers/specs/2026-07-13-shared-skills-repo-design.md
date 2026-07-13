# Shared Skills Repository — Design

Date: 2026-07-13
Status: validated by brainstorm, pending user review

## Problem

Four CLAUDE.md files carry massively duplicated, near-verbatim content:

- `TrueWallet/CLAUDE.md` (~380 lines) — the most advanced and up-to-date; **canonical source**.
- `Hermenea/CLAUDE.md` (~270 lines) — same Go standards, same commit convention, simplified pipeline.
- `BluePods/.claude/CLAUDE.md` (~270 lines) — same Go standards, same commit convention, single-repo pipeline variant.
- `Skills/CLAUDE.md` (~230 lines) — the Rust adaptation of the Go standards.

The duplicated blocks: Go Coding Standards (~110 lines ×3), the custom superpowers
feature pipeline (~60-90 lines ×3), the `[+]/[-]/[&]/[!]` commit convention (~30
lines ×3), the Justfile conventions (×2), and the "CLAUDE.md Design" meta-section (×4).

Two consequences:

1. **Drift.** Updates land in one file and not the others (Hermenea lacks the git
   workflow section; BluePods lacks go.mod hygiene and Justfile conventions).
2. **No distribution.** The duplicated content lives in parent-directory CLAUDE.md
   files that belong to no git repository. Collaborators cloning the individual
   repos (`TrueWallet-Backend`, etc.) receive none of it — their agents follow
   none of these standards today.

## Goals

- One public source of truth for shared standards: the `Skills` GitHub repository
  (`https://github.com/clemsix6/Skills`).
- Every collaborator's agent uses the **latest** version automatically — no manual
  update step. Freshness is explicitly chosen over version pinning (risk accepted:
  a bad push propagates instantly; fix forward).
- **Deterministic loading**: standards must reach the context without any model
  decision, including in implementer subagents (the custom pipeline is
  subagent-driven, so pull-based skills would silently miss the code writers).
- No sensitive data in the public repo.

## Non-goals

- Migrating projects beyond TrueWallet, BluePods, Hermenea, and the Rust style
  (Plumy, HopeAI, LLMGW, … can adopt the same mechanism later).
- Claude Code plugin/marketplace packaging (possible v2 if procedures multiply;
  rejected for v1 because plugin updates are manual and break the freshness goal).
- Version pinning, submodules, or per-project version selection.

## Design

### Mechanism overview

Two native Claude Code features compose the whole system:

1. **`@` imports** in each project's CLAUDE.md inline shared fragments at session
   start — deterministic, no model decision, and the content follows the context
   into subagents.
2. **A `SessionStart` hook** in each repo's committed `.claude/settings.json`
   keeps a local clone of the Skills repo fresh — deterministic, no reliance on
   the model remembering to pull.

### Clone location: `~/Skills` (fixed, home-relative)

One clone per machine, not per project:

- Imports use `@~/Skills/<fragment>.md` — the same path on every machine, so the
  same CLAUDE.md line works for every collaborator.
- No per-project `.gitignore` entry, no duplicated clones.
- **Worktree safety**: the TrueWallet/BluePods pipelines run implementation inside
  `.wt/<task>/` worktrees. A project-relative `./skills` clone would break there
  (the relative import would resolve inside the worktree, where no clone exists).
  A home-absolute path is immune.

On the owner's machine, `~/Skills` is this very repository (working copy = clone).

### The SessionStart hook

Each git repository commits `.claude/settings.json` containing:

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

Properties: clone-if-absent, fast-forward pull otherwise, silent tolerance of
offline mode (`|| true` keeps the local version). Concurrent sessions are safe
(git's own locking; `--ff-only` never rewrites). HTTPS URL because the repo is
public — no SSH key required to consume it.

### Fragments (6)

Flat `.md` files at the repo root. All content in English, generic only —
nothing project-specific, nothing sensitive.

| Fragment | Content | Extracted from | Imported by |
|---|---|---|---|
| `general.md` | Cross-project defaults: command runner = `just` (never Makefile/Taskfile) + Justfile writing conventions (quiet, minimal recipes, shebang recipes, conditional `GOWORK`); the "CLAUDE.md Design" meta-rules. Grows as new cross-cutting preferences appear. | TrueWallet | all projects |
| `go-style.md` | Go Coding Standards: KISS, minimal public API, documentation, code style, function/file size, TODO comments, go.mod hygiene, error wrapping, doc example. | TrueWallet | TrueWallet, Hermenea, BluePods (root) |
| `rust-style.md` | The current `Skills/CLAUDE.md` Rust standards, near-verbatim. | Skills | BluePods `pods/` and `wasm-gas/`, future Rust projects |
| `commit-convention.md` | Title line + `[+]/[-]/[&]/[!]` body, no footers. | identical ×3 | all projects |
| `git-workflow.md` | `main` as the only long-lived branch, `type/kebab-description` branches, squash-merge, PR lifecycle (draft after first push, body kept current, ready when CI is green); "work on the right code" rules — analyses and bug fixes start from the up-to-date default branch, `git fetch origin` before searching branches. | TrueWallet | all projects (new adoption for Hermenea) |
| `feature-pipeline.md` | The custom superpowers pipeline: the common steps (brainstorm → spec → spec review → autonomous fix → spec summary to the user → plan → plan+spec review → autonomous fix → implementation), plan rules (single phase, batches of ~1-5, 1 task = 1 commit), per-batch rules (build stays green, wiring per batch, critical-batch review, push per batch), and the generic single-repo task-workspace pattern (`.wt/<task>` worktree from `origin/main`, no CWD change, `-C` flag, cleanup at merge). States explicitly: *"The project CLAUDE.md may insert additional steps or override the workspace pattern."* | TrueWallet | TrueWallet, Hermenea, BluePods |

Non-imported files: `README.md` (how to wire a project: the import lines, the
hook, the one-time bootstrap) and the repo's own `CLAUDE.md` (editing rules for
the repo itself: English only, generic-only content, no secrets, fragments must
stay project-agnostic).

### Per-project wiring

Distribution to collaborators happens at the **git repository** level (that is
what they clone). Parent directories are the owner's local multi-repo
workspaces; their CLAUDE.md files also import fragments, for the owner's
multi-repo sessions.

**TrueWallet** (parent dir + one repo per service):

- `TrueWallet/CLAUDE.md` (parent, local): imports `general`, `go-style`,
  `commit-convention`, `git-workflow`, `feature-pipeline`; keeps locally — the
  Notion ticket step (inserted as an extra pipeline step, with the data-source
  IDs), the multi-repo task workspace override (`go.work`, one worktree per
  touched repo), deployment & release (MEP, staging validation, versioning,
  chained releases, rollback), tooling (gopls, Signoz), server access.
- Each service repo (`TrueWallet-Backend`, `TrueWallet-Entities`, …): its
  existing repo-specific CLAUDE.md gains the import lines at the top — `general`,
  `commit-convention`, `git-workflow`, `feature-pipeline` for every repo, plus
  `go-style` for Go repos (a repo with a `go.mod`) — and the repo commits
  `.claude/settings.json` with the hook. Repos without a CLAUDE.md get a minimal
  one holding just the imports. This is what makes the standards reach
  collaborators at all.

**Hermenea** (same parent-dir structure): parent CLAUDE.md imports the same five
fragments; keeps locally — `pkg/` package organization, hexagonal architecture
rules, database stack (pgx, sqlc, golang-migrate, schema ownership), testing
philosophy ("do not fake what you own", two speeds, deliberate seam, LLM testing
split). Service repos get imports + hook like TrueWallet's.

**BluePods** (single repo, mixed language):

- A committed root `CLAUDE.md` (the repo gitignores `.claude/` and had
  deliberately untracked `.claude/CLAUDE.md`, so a root file is what actually
  reaches collaborators): imports `general`, `go-style`, `commit-convention`,
  `git-workflow`, `feature-pipeline`; keeps locally — the VISION/WHITEPAPER
  pointers, documentation conventions, project layout, the batch rule extension
  (pods/wasm-gas builds must pass too). The local `.claude/CLAUDE.md` mirrors it
  until the adoption PR merges, then gets deleted.
- `pods/CLAUDE.md` and `wasm-gas/CLAUDE.md` (new, one line each):
  `@~/Skills/rust-style.md`. Claude Code loads subdirectory CLAUDE.md files on
  demand, so Rust style enters the context only when files in those subtrees are
  touched — Go-only sessions never carry it.
- Commits `.claude/settings.json` with the hook.

**Skills** (this repo): root `CLAUDE.md` is replaced by the repo-editing rules
(the Rust content moves to `rust-style.md`).

### Security policy

The repo is public. Fragments carry generic standards only. Everything
operational stays in project CLAUDE.md files: Notion data-source IDs, server
SSH access, staging/production URLs, deployment procedures, observability
endpoints.

## Edge cases

- **Fresh machine, first session**: the hook clones `~/Skills`, but the
  project CLAUDE.md was already loaded — imports of missing files are skipped
  for that one session. From the second session on, everything is active. The
  README documents the one-time manual bootstrap
  (`git clone https://github.com/clemsix6/Skills ~/Skills`) for a clean start.
- **Offline**: pull fails silently; the local version is used.
- **Existing `~/Skills` that is not this repo** (a collaborator's unrelated
  directory): the hook's clone fails silently and imports resolve to nothing or
  wrong files. The README states the requirement; this is accepted as a
  documented convention rather than engineered around.
- **Hook trust**: collaborators approve the hook when they first trust the
  project directory — standard Claude Code behavior, documented in the README.
- **Double loading on the owner's machine**: when a session runs inside a
  service repo, both the parent-directory CLAUDE.md and the repo CLAUDE.md are
  in context, each importing the same fragments — the content appears twice.
  Accepted: a few kilobytes, and it only affects the owner's local multi-repo
  setup (collaborators only have the repo level).

## Migration order

1. **Skills repo**: write the 6 fragments (canonical text from TrueWallet;
   Rust from the existing file), README, repo CLAUDE.md, publish public on
   GitHub as `clemsix6/Skills`.
2. **TrueWallet**: rewrite the parent CLAUDE.md (imports + local sections);
   add imports + hook to each service repo.
3. **Hermenea**: same.
4. **BluePods**: rewrite root CLAUDE.md, create the two subdirectory
   CLAUDE.md files, add the hook.

Each project migration is verifiable independently; TrueWallet goes first as
the source of truth (its behavior must not change).

## Validation

- In each migrated project, start a fresh session and check the imported rules
  are active (ask the agent to state, e.g., the commit convention and the
  function-size limit, without opening any file).
- Verify a session inside a `.wt/` worktree still receives the fragments.
- Verify a BluePods Go-only session does not carry the Rust style, and that
  touching `pods/` loads it.
- Break the network and start a session: the hook must not block or fail the
  session.
- Diff check: the concatenation of (fragments + local sections) against the old
  CLAUDE.md files — no rule silently lost.
