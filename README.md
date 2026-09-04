# Skills

Shared engineering standards for my projects: instruction fragments consumed
through CLAUDE.md `@` imports, plus the subagent definitions the pipeline
dispatches. One clone per machine, at `~/Skills`, kept fresh automatically —
every agent on every machine follows the latest version.

## One-time setup (per machine)

```bash
git clone https://github.com/clemsix6/Skills ~/Skills
```

Then add this `SessionStart` hook to `~/.claude/settings.json` — **user scope,
not per project.** It pulls the clone and installs the subagent definitions into
`~/.claude/agents/skills/`. Both are user-level paths, so one copy serves every
project and there is nothing to keep in sync:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "if [ -d \"$HOME/Skills/.git\" ]; then git -C \"$HOME/Skills\" pull --ff-only --quiet || echo 'Skills: pull failed, this machine is running an older copy' >&2; else git clone --quiet https://github.com/clemsix6/Skills \"$HOME/Skills\" || echo 'Skills: clone failed' >&2; fi; if [ -d \"$HOME/Skills/agents\" ]; then mkdir -p \"$HOME/.claude/agents\" && rm -rf \"$HOME/.claude/agents/.skills-new\" && cp -R \"$HOME/Skills/agents\" \"$HOME/.claude/agents/.skills-new\" && rm -rf \"$HOME/.claude/agents/skills\" && mv \"$HOME/.claude/agents/.skills-new\" \"$HOME/.claude/agents/skills\"; fi"
          }
        ]
      }
    ]
  }
}
```

The install copies to a staging directory first and only swaps it in once the
copy succeeded, so a failed or interrupted pull leaves the previous definitions
in place rather than uninstalling the pipeline silently. It is a replace, so a
definition deleted here disappears everywhere at the next session, and it only
ever touches `~/.claude/agents/skills/` — personal agents living directly under
`~/.claude/agents/` are left alone.

If a dispatch ever fails with an unknown agent type, this install is why: check
that `~/.claude/agents/skills/` exists and restart the session.

Older per-project copies of this hook may still sit in wired repos. They only
pull the clone, never install, so they are harmless duplicates of the first half
— but they are also why the user-scope hook is the one to edit when this changes.

## Wiring a project

Add the import lines at the top of the project's `CLAUDE.md` (create the file if
the repo has none):

```
@~/Skills/general.md
@~/Skills/go-style.md
@~/Skills/commit-convention.md
@~/Skills/git-workflow.md
@~/Skills/feature-pipeline.md
```

That is the whole wiring — the hook is already installed at user scope.

`feature-pipeline.md` assumes the [superpowers](https://github.com/obra/superpowers)
skills are installed — its first steps call the `brainstorming` skill and the
standard spec and plan formats. Import it only into projects that have them.

Drop `go-style` for non-Go repos. For Rust code, import
`@~/Skills/rust-style.md` — in a mixed repo, put that line in a
`CLAUDE.md` inside the Rust subdirectory so it loads only when Rust files
are touched. Projects that keep a graphify knowledge graph also import
`@~/Skills/graphify.md` (inert when `graphify-out/` is absent).

Projects the owner directs without reading the code import `@~/Skills/vibe.md`.
It keeps code out of Claude's replies, so leave it out of any repo whose owner
reviews diffs.

## Fragments

| File | Contents |
|---|---|
| `general.md` | Cross-language defaults: command runner (just), comment rules, CLAUDE.md design rules |
| `go-style.md` | Go coding standards |
| `rust-style.md` | Rust coding standards |
| `commit-convention.md` | Commit message format |
| `git-workflow.md` | Branching model and PR lifecycle |
| `feature-pipeline.md` | The feature-development pipeline: steps, plan rules, dispatch and scope |
| `graphify.md` | Knowledge-graph usage: query-first, update discipline (projects with a graph only) |
| `vibe.md` | Tone and formatting: outcome first, plain prose, no code in replies (vibe-coded projects only) |

## Agents

`agents/` holds the subagent definitions `feature-pipeline.md` dispatches by
name. They are installed at user scope by the hook above, so a wired project
needs no `.claude/agents/` of its own and every project gets them at once.

| Definition | Model | Effort | Role |
|---|---|---|---|
| `pipeline-spec-plan-review` | inherit | high | Reviews spec and plan together — the only gate before code exists |
| `pipeline-batch-review` | inherit | high | Reviews the diff of a batch the plan marks `review`, before the rest of the feature builds on it |
| `pipeline-implement` | sonnet | inherit | Implements one batch whole, reading the plan and spec from the repo itself |
| `pipeline-final-review` | opus | max | Reviews the assembled feature before the PR goes to a human — coverage, cross-batch coherence, accumulated drift |
| `implement` | sonnet | inherit | Implements one decided change outside the pipeline — a fix, a small change — from the exact change and the verification commands it is given; no commit |

Effort follows how much each pass holds at once: the final review sees the whole
feature and the whole diff, so it runs at `max`; the two earlier gates read two
documents and one batch's diff.

Neither gate pins a model, on purpose — both inherit the session's, so a session
running on the strong model gets strong gates and one deliberately running cheap
is not dragged back up.

`pipeline-batch-review` is the only conditional agent: it is dispatched for a
batch the plan marks `review` and for no other. The mark is a plan-level
decision because a runtime one defaults to "not sensitive" every time, and it is
capped at two per feature — a pipeline that reviews every batch is the one this
one deliberately replaced.

Colour is display only — it groups agents by the kind of work they do so a run is
readable at a glance: `blue` for the review whose subject is a document, `orange`
for the reviews whose subject is a diff, `green` for implementation. It carries
no behaviour and enforces nothing.

Nothing below the orchestrator dispatches: the three reviewers and
`pipeline-implement` are denied `Agent`, so no agent can fan out. That part is
structural.

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
`feature-pipeline.md`, which loads into all four agents and should carry only
what one of them acts on.

- **Nesting.** The pipeline is two levels: session → reviewer or implementation
  agent. That is one subagent layer, well inside the default spawn depth of
  three (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`).
- **`background`.** Subagents run in the background by default; the platform
  moves one to the foreground when its caller needs the result before continuing.
  No definition sets the field: the background filter strips built-in tools, but
  every tool these agents hold — `Read`, `Grep`, `Glob`, `Bash`, `Edit`,
  `Write` — is on the kept list, so the value would change nothing for them.
- **Withholding `Agent`.** Use an explicit `tools` list or `disallowedTools`;
  the `Agent(type)` allowlist syntax has no effect inside a subagent definition.
- **Caps.** 200 subagents per session, 20 concurrent. The pipeline dispatches
  one agent at a time and a feature costs a handful in total, so neither binds.
  Hitting the session cap produces an error telling the caller to do the work
  itself — the pipeline says to take that to the supervisor instead.
- **Effort** is frontmatter-only, with no dispatch-time equivalent. `model` can
  be set at either, and the dispatch parameter wins; `CLAUDE_CODE_SUBAGENT_MODEL`
  only fills in when neither is set (since 2.1.251 — before that it beat both).
- **Model aliases** resolve through the environment: `sonnet` in a definition
  means whatever `ANTHROPIC_DEFAULT_SONNET_MODEL` names for that session. That
  is how the same definitions run on the vendor's models under one alias and on
  a third-party pair under another (see "The lab runner").

## The lab runner

A session can run on two models: the main thread on a strong one, the `sonnet`
and `haiku` tiers on a lighter one several times cheaper. `pipeline-implement`
and `implement` are declared `sonnet`, a browser driver like socialflow's
`capture` agent `haiku`, the reviews `inherit` or `opus` — the split is already
in the definitions; what a session chooses is what the aliases mean.

The pair has one job: a project's `lab/` (socialflow's, today), where a GLM
thread captures, replays, reverses and measures, and hands off to Claude Opus
through a document. Two pieces:

- **`glm-lab.md`** — appended to the system prompt with
  `--append-system-prompt-file`. The thread writes its own probes, journal and
  state; dispatches `implement` for anything larger than a probe and `capture`
  for every browser session; never writes under the product's directories.
- **`hooks/delegate-edits.py`** — a `PreToolUse` hook for a session that must
  not write code at all: it refuses `Edit`/`Write`/`MultiEdit`/`NotebookEdit`
  on a code file from the main thread and tells it to dispatch `implement`.
  Inert unless the session exports `CLAUDE_DELEGATE_EDITS=1`; subagents pass
  (their calls carry `agent_id`), and so do Markdown, text, anything under
  `docs/` and the scratch locations briefs and reports go to. It does not see
  a `sed` or a heredoc run through `Bash`. The lab runner does not set it —
  the lab writes — but a review or triage thread on a light model can.

Register the hook once per machine, user scope, next to the `SessionStart`
hook above:

```json
"PreToolUse": [
  {
    "matcher": "Edit|Write|MultiEdit|NotebookEdit",
    "hooks": [{ "type": "command", "command": "\"$HOME/Skills/hooks/delegate-edits.py\"" }]
  }
]
```

- **`hooks/capture-agent-only.py`** — a `PreToolUse` hook that refuses any
  `mcp__capture__*` tool on the main thread and lets the `capture` subagent
  through, so only the agent drives the browser. Armed by
  `CLAUDE_CAPTURE_AGENT_ONLY=1`, which the lab runner sets. It exists because
  `--disallowedTools mcp__capture` was measured to strip the tools from
  subagents too (4 September 2026). Register it next to the edit hook:

```json
"PreToolUse": [
  {
    "matcher": "mcp__capture__.*",
    "hooks": [{ "type": "command", "command": "\"$HOME/Skills/hooks/capture-agent-only.py\"" }]
  }
]
```

The lab alias — the vendor alias (`cc`) sets none of it and is untouched:

```bash
alias glm='ANTHROPIC_BASE_URL=<anthropic-compatible endpoint> \
ANTHROPIC_AUTH_TOKEN=<key> \
ANTHROPIC_DEFAULT_OPUS_MODEL="<strong model>[1m]" \
ANTHROPIC_DEFAULT_SONNET_MODEL="<light model>[1m]" \
ANTHROPIC_DEFAULT_HAIKU_MODEL="<light model>[1m]" \
CLAUDE_CAPTURE_AGENT_ONLY=1 \
claude --dangerously-skip-permissions --append-system-prompt-file ~/Skills/glm-lab.md'
```

The `[1m]` suffix matters for a model Claude Code does not know: without it
the context window is assumed to be 200k and compaction fires five times too
early; with it the suffix is stripped before the request and the window is
taken as one million.

## Rules of this repo

Fragments are generic: no project names, no credentials, no internal URLs or
IDs. Project-specific rules live in each project's own CLAUDE.md. Updates land
on `main` and propagate to every machine at the next session start.
