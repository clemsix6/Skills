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
`@~/Skills/graphify.md` (inert when `graphify-out/` is absent). Projects with
a kanban tenant also import `@~/Skills/kanban-tickets.md` and declare
`tenant`, `workflow` and `label` in their own CLAUDE.md (see that fragment).

Projects the owner directs without reading the code import `@~/Skills/vibe.md`.
It keeps code out of Claude's replies, so leave it out of any repo whose owner
reviews diffs.

## Fragments

| File | Contents |
|---|---|
| `general.md` | Cross-language defaults: command runner (just), comment rules, CLAUDE.md design rules; imports `subagent-models.md` and `workflows.md` |
| `subagent-models.md` | Which model and effort each subagent gets, in a pipeline or not — loaded through `general.md`, never imported directly |
| `workflows.md` | When a workflow beats subagents, and how to offer one — loaded through `general.md`, never imported directly |
| `go-style.md` | Go coding standards |
| `rust-style.md` | Rust coding standards |
| `commit-convention.md` | Commit message format |
| `git-workflow.md` | Branching model and PR lifecycle |
| `feature-pipeline.md` | The feature-development pipeline: steps, plan rules, dispatch and scope |
| `kanban-tickets.md` | Kanban board conventions: the `po` event contract, epic/PR linking (projects with a kanban tenant only) |
| `graphify.md` | Knowledge-graph usage: query-first, update discipline (projects with a graph only) |
| `vibe.md` | Tone and formatting: outcome first, plain prose, no code in replies (vibe-coded projects only) |

## PO command (`po`)

`bin/po` sends the feature pipeline's fixed checkpoints (see
`kanban-tickets.md`) to Hermes' PO over its oneshot channel — spec approved,
plan validated, batch pushed, blocked, spec adjusted, out-of-scope findings,
final verdict, abandoned. Install it once per machine, next to the
`SessionStart` hook above:

```bash
mkdir -p ~/.local/bin
ln -sf ~/Skills/bin/po ~/.local/bin/po
```

`~/.local/bin` must be on `PATH`. By default `po` talks to Hermes over SSH,
opening a connection to `$PO_SSH_HOST` (default `hermes-po`): an alias the
admin sets up in `~/.ssh/config`, pointing at the Hermes host with a key it
authorizes. Without that alias, set `PO_SSH_HOST=user@host` instead.

Direct transport — calling a local `hermes` binary instead of ssh — is
opt-in only, via `PO_TRANSPORT=direct`: a `hermes` binary merely being on
`PATH` is never enough on its own, since it could be an unrelated local
tool. The host that actually hosts Hermes (missions on the server, where
`po` runs already scoped to that host) installs a small wrapper ahead of
`po` on `PATH` that does:

```bash
exec env PO_TRANSPORT=direct <clone>/bin/po "$@"
```

Usage:

```bash
po open --project <tenant> --title "..." --body-file spec-summary.txt
po batch --project <tenant> --epic t_xxx <<'EOF'
batch 2/4: ...
EOF
```

Run `po --help` for the full flag, transport and exit-code reference; set
`PO_DRY_RUN=1` to see the composed message without sending it.

## Agents

`agents/` holds the subagent definitions `feature-pipeline.md` dispatches by
name. They are installed at user scope by the hook above, so a wired project
needs no `.claude/agents/` of its own and every project gets them at once.

| Definition | Model | Effort | Role |
|---|---|---|---|
| `pipeline-spec-plan-review` | opus | high | Reviews spec and plan together — the only gate before code exists |
| `pipeline-batch-review` | opus | high | Reviews the diff of a batch the plan marks `review`, before the rest of the feature builds on it |
| `pipeline-implement` | sonnet | medium | Implements one batch whole, reading the plan and spec from the repo itself |
| `pipeline-final-review` | opus | max | Reviews the assembled feature before the PR goes to a human — coverage, cross-batch coherence, accumulated drift |
| `implement` | sonnet | medium | Implements one decided change outside the pipeline — a fix, a small change — from the exact change and the verification commands it is given; no commit |

Effort follows how much each pass holds at once: the final review sees the whole
feature and the whole diff, so it runs at `max`; the two earlier gates read two
documents and one batch's diff. The implementers pin `medium`, the documented
starting point for well-specified agentic coding on Sonnet: unpinned, they would
run at the session's effort, and Sonnet at `xhigh` or `max` is slow and costly
for work a plan already specifies.

Every definition pins its model, because `inherit` hands a subagent the
session's model — a Fable subagent on a Fable session, which `subagent-models.md`
forbids unless the user asks. Reviews pin `opus`, implementation `sonnet`.

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
carry `effort` and pinned `tools`, which no Agent-tool parameter can set.

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
  three (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`). A review workflow's agents
  sit on that same layer: the script is not an agent.
- **`background`.** Subagents run in the background by default; the platform
  moves one to the foreground when its caller needs the result before continuing.
  No definition sets the field: the background filter strips built-in tools, but
  every tool these agents hold — `Read`, `Grep`, `Glob`, `Bash`, `Edit`,
  `Write` — is on the kept list, so the value would change nothing for them.
- **Withholding `Agent`.** Use an explicit `tools` list or `disallowedTools`;
  the `Agent(type)` allowlist syntax has no effect inside a subagent definition.
- **Caps.** 200 subagents per session, 20 concurrent. The pipeline dispatches
  one agent at a time and a feature costs a handful in total, so neither binds;
  review workflows add a few dozen at most, run under the Workflow runtime's
  own concurrency limit.
  Hitting the session cap produces an error telling the caller to do the work
  itself — the pipeline says to take that to the supervisor instead.
- **Effort** has no Agent-tool parameter: a dispatch gets the definition's, or
  the session's when the definition pins none. A workflow script's `agent()`
  does take `effort` per call. `model` can be set at either, and the dispatch
  parameter wins; `CLAUDE_CODE_SUBAGENT_MODEL`
  only fills in when neither is set (since 2.1.251 — before that it beat both).
- **Model aliases** resolve through the environment: `sonnet` in a definition
  means whatever `ANTHROPIC_DEFAULT_SONNET_MODEL` names for that session. That
  is how the same definitions run on the vendor's models under one alias and on
  a third-party pair under another (see "The lab runner").

## Subagent models

`subagent-models.md` holds the rules; this is the evidence behind them,
measured on Opus 5.5 and Sonnet 5.5 in September 2026. Re-check it when a new
model generation ships — effort levels are recalibrated between generations.

Sources:

- Anthropic, *Building with Claude Sonnet 5.5* —
  https://claude.dev/blog/building-with-claude-sonnet-5-5/
- Anthropic, *Using Claude Code: Spending your effort* —
  https://claude.dev/blog/spending-your-effort/
- Bug Hunt Bench — 105 bugs planted in two production repos, one "find and fix
  what you can" prompt per repo, graded blind against a withheld answer key —
  https://bughunt.productcompass.pm, raw data in
  https://github.com/phuryn/bug-hunt-bench

What they establish:

- **Sonnet for well-scoped work, Opus for judgment.** Anthropic's own split:
  Sonnet for well-scoped coding, verifying against requirements, documents, and
  well-defined agent tasks run repeatedly (investigation, review, drafting);
  Opus for complex work requiring careful judgment, long-horizon agentic work,
  and the hardest problems. Sonnet "fits best when the task has a clear spec and
  a way to check the result". Review and investigation stay on Opus here: the
  reviews are the gates the pipeline relies on, and investigation means
  diagnosis, not lookup.
- **Effort buys thoroughness, not judgment.** On Terminal-Bench 3.0, raising
  Fable 5.1 from low to max cut "missed a case" failures from 59 to 24 but
  "made the wrong call" only from 133 to 107 — "picked the wrong reading" rose
  from 25 to 47. Effort pays most on edge-case-heavy work (security 64 → 87 %,
  hardware 34 → 75 %) and least on rulebook work (operations 12 → 22 %).
- **Opus 5.5 flattens after `medium`**: roughly 36 % at low, 54 % at medium,
  59 % at high, 62 % at xhigh, 65 % at max on Terminal-Bench 3.0, each step
  costing markedly more tokens. At high it matches Fable 5.1 at max for half the
  tokens.
- **No user in the loop favours higher effort**: at low, the model picks a
  plausible reading and reports; at high it tries alternatives and checks them.
  A detailed spec narrows the gap between levels.
- **Sonnet 5.5 at `low` sometimes skips the check that exercises a change.**
  Anthropic's starting points: `medium` for well-specified agentic coding,
  `high` for harder or longer work, `xhigh`/`max` only where evals show a gain —
  there Sonnet "will think longer and cost more", and Opus may be the better
  choice. Claude Code runs Sonnet 5.5 at `medium` by default.
- **Exhaustive bug hunting is the exception.** Bug Hunt Bench, Claude Code
  runs, planted bugs fixed out of 105:

| Effort | Sonnet 5.5 | Opus 5.5 (mean of 3 runs) |
|---|---|---|
| low | 20 · 7 min · $6 | 22.3 · 12 min · $8 |
| medium | 18 · 12 min · $8 | 30.3 · 17 min · $16 |
| high | 32 · 24 min · $17 | 31.7 · 24 min · $22 |
| xhigh | 39 · 122 min · $60 | 36 · 42 min · $35 |
| max | 55.5 (runs of 57 and 54) · 235 min · $135 | 41.7 · 67 min · $59 |

Sonnet rows are single runs except `max`, and the bench measures about ten
points of spread on one configuration. Sonnet at `max` leads every model
measured by persistence, not insight: about 1,330 turns against 476 for Opus at
`max`, for 3.5× the time and 2.3× the cost. Below `max` it has no edge, and at
`medium` — where the agent must decide where to look on its own — it clearly
trails Opus. Its unplanted fixes (24.5 against 9) track that volume and the
model family's style — GPT runs fix 40 to 55 — not judgment.

## Workflows

`workflows.md` holds the rules; this is the evidence behind them, as of
September 2026. Re-check it when the Workflow tool changes — its opt-in rule
and its limits are the parts most likely to move.

Sources:

- Claude Code docs, *Orchestrate subagents at scale with dynamic workflows* —
  https://code.claude.com/docs/en/workflows
- Claude Code docs, *Run agents in parallel* —
  https://code.claude.com/docs/en/agents
- Anthropic, *Introducing dynamic workflows* (May 2026) —
  https://claude.com/blog/introducing-dynamic-workflows-in-claude-code
- Claude Cookbook, *Orchestrate subagents at scale with dynamic workflows* —
  https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows
- Anthropic, *How we built our multi-agent research system* —
  https://www.anthropic.com/engineering/multi-agent-research-system

What they establish:

- **The difference is who holds the plan.** With subagents Claude decides turn
  by turn and every result lands in its context; a workflow's script holds the
  loop, the branching and the intermediate results, so only the final answer
  comes back — and a quality pattern (adversarial verification, independent
  attempts) runs because the code says so.
- **When it pays.** The cookbook's test: "the task outgrows one context window
  (many items, many sources), needs verification you can't afford to skip, or
  is a process you'll repeat" — while for a single agent, "most tasks live
  here". The docs add a hard plan drafted from several independent angles.
- **Coupled work is the poor fit.** Multi-agent systems struggle where agents
  must share one context or depend heavily on each other, and "most coding
  tasks involve fewer truly parallelizable tasks than research". That is why
  only the pipeline's two reviews can become workflows, never its
  implementation.
- **Claude cannot opt in for the user.** The Workflow tool's own description
  allows a run only on an explicit opt-in: the `ultracode` keyword, ultracode on
  for the session, a direct request in the user's words, a skill or command the
  user invoked that calls for one, or a saved workflow the user named. A
  CLAUDE.md rule is none of these, and the docs count the keyword only in a
  prompt a human typed — not `-p`, a scheduled task or a relayed webhook. Hence
  propose-then-run, and the offer at the pipeline's one human gate.
- **Cost.** Multi-agent systems used about 15× the tokens of a chat in
  Anthropic's research system; the cookbook's ten-claim fact-check took about
  550k tokens and $3.29. Claude Code flags a run past 25 agents or 1.5M
  projected tokens, and by default aims under 10 agents (the `medium` size
  guideline in `/config`). The docs' advice: run a slice first.

## The lab runner

A session can run on two models: the main thread on a strong one, the `sonnet`
and `haiku` tiers on a lighter one several times cheaper. `pipeline-implement`
and `implement` are declared `sonnet`, a browser driver like socialflow's
`capture` agent `haiku`, the reviews `opus` — the split is already
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
