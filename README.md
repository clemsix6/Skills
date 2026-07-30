# Skills

Shared engineering standards for my projects: instruction fragments consumed
through CLAUDE.md `@` imports, plus the subagent definitions the pipeline
dispatches. One clone per machine, at `~/Skills`, kept fresh automatically —
every agent on every machine follows the latest version.

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

   `feature-pipeline.md` assumes the [superpowers](https://github.com/obra/superpowers)
   skills are installed — its first steps call the `brainstorming` skill and the
   standard spec and plan formats. Import it only into projects that have them.

   Drop `go-style` for non-Go repos. For Rust code, import
   `@~/Skills/rust-style.md` — in a mixed repo, put that line in a
   `CLAUDE.md` inside the Rust subdirectory so it loads only when Rust files
   are touched. Projects that keep a graphify knowledge graph also import
   `@~/Skills/graphify.md` (inert when `graphify-out/` is absent).

2. Commit `.claude/settings.json` with the SessionStart hook. It refreshes the
   clone and installs the subagent definitions into `~/.claude/agents/skills/`:

   ```json
   {
     "hooks": {
       "SessionStart": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "if [ -d \"$HOME/Skills/.git\" ]; then git -C \"$HOME/Skills\" pull --ff-only --quiet || echo 'Skills: pull failed — this machine is running an older copy' >&2; else git clone --quiet https://github.com/clemsix6/Skills \"$HOME/Skills\" || echo 'Skills: clone failed' >&2; fi; if [ -d \"$HOME/Skills/agents\" ]; then mkdir -p \"$HOME/.claude/agents\" && rm -rf \"$HOME/.claude/agents/.skills-new\" && cp -R \"$HOME/Skills/agents\" \"$HOME/.claude/agents/.skills-new\" && rm -rf \"$HOME/.claude/agents/skills\" && mv \"$HOME/.claude/agents/.skills-new\" \"$HOME/.claude/agents/skills\"; fi"
             }
           ]
         }
       ]
     }
   }
   ```

   The install copies to a staging directory first and only swaps it in once the
   copy succeeded, so a failed or interrupted pull leaves the previous
   definitions in place rather than uninstalling the pipeline silently. It is a
   replace, so a definition deleted here disappears everywhere at the next
   session, and it only ever touches `~/.claude/agents/skills/` — personal
   agents living directly under `~/.claude/agents/` are left alone.

   If a dispatch ever fails with an unknown agent type, this install is why:
   check that `~/.claude/agents/skills/` exists and restart the session.

## Fragments

| File | Contents |
|---|---|
| `general.md` | Cross-language defaults: command runner (just), CLAUDE.md design rules |
| `go-style.md` | Go coding standards |
| `rust-style.md` | Rust coding standards |
| `commit-convention.md` | Commit message format |
| `git-workflow.md` | Branching model and PR lifecycle |
| `feature-pipeline.md` | The feature-development pipeline (superpowers custom) |
| `graphify.md` | Knowledge-graph usage: query-first, update discipline (projects with a graph only) |

## Agents

`agents/` holds the subagent definitions `feature-pipeline.md` dispatches by
name. They are installed at user scope by the hook above, so a wired project
needs no `.claude/agents/` of its own and every project gets them at once.

| Definition | Model | Effort | Role |
|---|---|---|---|
| `pipeline-spec-review` | opus | xhigh | Reviews the spec against the intent it came from, before the human checkpoint |
| `pipeline-plan-review` | opus | xhigh | Reviews the whole plan against the spec — coverage, batching, ordering, annotations |
| `pipeline-batch-manager` | opus | inherit | Owns one batch end to end: precondition check, reviews, implementation dispatch, fix, push |
| `pipeline-batch-plan-review` | opus | high | Hunts for defects in one batch's plan, in a narrow scope and with the previous batches' real code as context |
| `pipeline-implement` | sonnet | inherit | Implements one task, reading the plan and spec from the repo itself |
| `pipeline-batch-review` | opus | high | Reviews an implemented batch's full diff, focused on consistency across tasks written by different agents |
| `pipeline-final-review` | opus | max | Reviews the assembled feature before the PR goes to a human — coverage, cross-batch coherence, accumulated drift |

Naming: a review named for its subject alone is global (`plan-review` covers the
whole plan), a `batch-` prefix scopes it to one batch. Effort follows that
split, since a whole-subject review has the most to hold at once.

Colour is display only — it groups agents by the kind of work they do so a run is
readable at a glance: `blue` for reviews whose subject is a document, `orange`
for reviews whose subject is a diff, `green` for implementation, `purple` for the
batch-manager. It carries no behaviour and enforces nothing.

Only `pipeline-batch-manager` dispatches: the five reviewers and
`pipeline-implement` are all denied `Agent`, so none of them can fan out. That
part is structural.

Two things are not. Read-only is a prompt constraint — the reviewers hold `Bash`
because they need `git`, `gh` and the build, and `Bash` can write. And
`pipeline-implement` inherits every configured MCP server, so in a project wired
to a GitHub server it holds tools that can push or merge; only its prompt stops
it. A project that wants either guarantee enforced needs a `PreToolUse` hook.
Treat a violation as a bug to fix, not as something the configuration prevents.

They are definitions rather than dispatch-time prompts because a subagent's
system prompt *is* its definition body — on `general-purpose`, every role's
protocol would be rewritten by its caller at each dispatch. Definitions also
carry `effort` and pinned `tools`, which no dispatch parameter can set.

CLAUDE.md loads in every custom subagent, so these bodies hold role protocol
only: the fragments imported by the project supply code style, commit format
and the rest.

The hook replaces `~/.claude/agents/skills/` on every session start, and the
directory watcher only covers directories that existed when the session began —
so treat definitions as loading at session start, not live. After changing one,
restart the session before relying on it.

### Platform notes

Reference for maintaining these definitions — deliberately kept out of
`feature-pipeline.md`, which loads into all seven agents and should carry only
what one of them acts on.

- **Nesting.** The pipeline is three levels: session → batch-manager → review
  and implementation agents. That is two subagent layers, within the default
  spawn depth of three. If a batch-manager cannot spawn, check
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`.
- **`background`.** Subagents run in the background by default; the platform
  moves one to the foreground when its caller needs the result before continuing.
  Only `pipeline-batch-manager` sets the field, to `true`, so the conversation
  stays usable while a batch runs. The others leave it unset: the background
  filter strips built-in tools, but every tool they hold — `Read`, `Grep`,
  `Glob`, `Bash`, `Edit`, `Write` — is on the kept list, so the value would
  change nothing for them.
- **Withholding `Agent`.** Use an explicit `tools` list or `disallowedTools`;
  the `Agent(type)` allowlist syntax has no effect inside a subagent definition.
- **Caps.** 200 subagents per session, 20 concurrent, nested ones counted. A
  three-batch feature peaks around six concurrent and thirty total, so neither
  binds in practice. Hitting the session cap produces an error telling the
  caller to do the work itself — the pipeline says to treat that as a blocked
  batch instead.
- **Effort** is frontmatter-only, with no dispatch-time equivalent. `model` can
  be set at either, and the dispatch parameter wins — except against
  `CLAUDE_CODE_SUBAGENT_MODEL`, which beats both.

## Rules of this repo

Fragments are generic: no project names, no credentials, no internal URLs or
IDs. Project-specific rules live in each project's own CLAUDE.md. Updates land
on `main` and propagate to every machine at the next session start.
