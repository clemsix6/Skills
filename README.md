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
