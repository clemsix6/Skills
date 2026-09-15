## Kanban Tickets

Applies when the consuming project's CLAUDE.md declares a kanban tenant. The
board is the team's shared brain, and Hermes — never Claude Code directly —
is the one who reads and writes it: every card comes from a `po` call to
Hermes' PO, or from the automated watchdog that turns build and deploy
activity into cards. Three principles survive from the previous board
unchanged: **complete, forward-only, keep it true.** Dropped: a mandatory
human assignee on every card, and a separate Pull Requests base — a PR is
tracked by the `Issue:` line in its own body, not by a row elsewhere.

### No PR without an epic

Every feature — even a single-PR one — opens with `po open` before any code
is written; Hermes creates one **epic** card and returns its id (`t_xxx`).
Every PR the feature produces carries `Issue: t_xxx` at the top of its body.
`Issue: none` does not exist anymore: if a PR has no epic yet, open one
before the PR is marked ready, never after. The watchdog reads that line to
file the PR's own card as the epic's child instead of an orphan — do not
paraphrase it, move it, or bury it below other content.

### The `po` command

A fixed, closed list of events carries the pipeline's fixed points to
Hermes — see `po --help` for flags, transport and exit codes. Every call is
its own message: the PO's channel has no memory of any earlier call, so
nothing is implied — tenant, epic id and the full body ride along every time.

| Event | Body must contain |
|---|---|
| `open` | Objective (1 paragraph), scope (in/out), repos touched, spec link or commit SHA, batch count if known |
| `plan` | Batch count, one line per batch |
| `batch` | k/N, a **product** summary (not a file list), the PRs touched |
| `blocked` | The reason, the question, who it is for |
| `adjust` | What changed, whether it was autonomous or supervisor-approved, the new scope if approved |
| `issues` | One short title + one sentence per out-of-scope finding sent to the backlog |
| `review` | The final review's verdict, the list of PRs |
| `abandon` | The reason |
| `ask` | A free-form question — the only event with no fixed body shape |

`open` and `ask` are the only events that skip `--epic`; every other event
needs the id an earlier `open` returned, or the call is rejected outright.
There is no `--assignee` — `--author` says who the event belongs to, and
Hermes uses it as the epic's owner at `open` and as the actor on every
comment after.

Hermes' reply ends with a line `epic: t_xxx` — the id it just created for
`open`, or the id you passed in for every other event. Capture it: pass it as
`--epic` to the feature's next `po` call, and drop it into every PR the
feature opens as `Issue: t_xxx`.

### Complete — no half-epics

An epic missing one of `open`'s required pieces doesn't describe the
feature yet. If the scope, the repos touched, or the spec link is missing or
doubtful, ask before calling `open` — a half-epic misleads the board worse
than a late one.

### Forward-only, still

The epic mirrors the feature's real progress — `running` while code is
being written, `review` once every PR it owns has reached review, `done`
once all of them have shipped. That roll-up is the watchdog's job, not
`po`'s: a `po` call reports what happened, it does not push the epic through
the deploy pipeline by itself. Never invent a shortcut around a roll-up that
looks stuck — fix what is stuck instead of front-running it.

### Keep it true

`po adjust` exists because scope drifts: when the objective, the scope, or
the repos touched change materially, say so through it rather than letting
the epic quietly describe a feature that no longer matches the PRs landing
under it.

### A failed `po` never blocks

Transport can fail or time out — a flaky link, a busy PO. When it does, note
it (in the PR body, under `Known issues` if nothing more specific fits) and
keep going. The board falling one event behind is recoverable; a feature
stalled on a kanban call is not an acceptable trade.

### What the project declares

The consuming project's CLAUDE.md states three things, and only there — this
fragment stays agnostic to all of them:

- **`tenant`** — the kanban tenant this project's cards belong to.
- **`workflow`** — `staging-then-prod` (an epic reaches `review` once staged,
  `done` once released to prod) or `direct-to-done` (a green merge is both at
  once).
- **`label`** — the short prefix the activity feed uses for this project's
  lines.
