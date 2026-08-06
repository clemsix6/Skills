## Notion Tickets

Applies when the consuming project's CLAUDE.md declares a Notion task board
(a data-source id and a `Project` select value). The board is the team's shared
brain: a ticket that is a bare title, has no owner, or lies about its status
makes the board worse than useless. Three principles: **complete, owned,
forward-only.**

### No PR without a ticket

Every PR references a ticket via an `Issue: <notion page url>` line at the top
of the PR body. Whoever holds the context at creation time writes the ticket —
if you ran the brainstorm or the fix, you create it (at latest when the PR
opens). **Check for an existing ticket first**: work arriving through an intake
flow may already have one — refresh its body instead of duplicating it.

### Complete — a ticket missing pieces doesn't exist yet

- **Title**: short (≤ ~6 words). The pitch goes in the body, never the title.
- **Body**: headings Objectif / Scope / Description, never empty.
- **Project**: the consuming project's declared select value.
- **Priority** (and **Area** where the project defines one): infer from the
  subject; genuinely unclear → ask.
- **Assignee**: mandatory, see below.

If something required is missing or doubtful, ask before creating — no
half-tickets.

### Owned — every ticket has an assignee

- Born from a PR or push → the **PR author**, mechanically.
- Anything else → the human the work belongs to; the slightest doubt → ask.
  Resolve Notion user ids at runtime through the users API (`GET /v1/users`),
  matching by name or email — **never invent a user id**, and never assign a
  bot.
- **Contributors accumulate**: every contributor of a linked PR belongs on the
  ticket — add on the next touch, add-only, never remove.
- ⚠️ A people PATCH **replaces** the whole array: always GET current ids and
  PATCH the union. Identical array → skip the write.

### Forward-only — the status mirrors the deploy pipeline

The project's CLAUDE.md maps board statuses to its own pipeline (e.g. merge →
staging → prod, or merge = prod directly). Never regress a status: shipped work
doesn't un-ship. If the project has an automated watcher moving statuses,
don't front-run it — its feed lines are generated from the very transition you
would steal; fix a status forward yourself only when it is visibly stale.

### Link both ways

`Issue:` line in the PR body, and the PR upserted in the project's Pull
Requests data source (one page per PR URL — check it doesn't already exist)
with Name, URL, Author, Repo, Project, the Ticket relation, and `Merged at`
once merged.

### Keep it true

The ticket mirrors the CURRENT intent. When objective, scope, or approach
changes materially, whoever holds the context updates the body (and title if
it no longer fits). A stale ticket misleads the board as much as a missing one.

### Mechanics

Multi-data-source boards need API version `2025-09-03`: use your Notion tools
if they can target the data source, else REST — `POST /v1/pages` with parent
`{"type": "data_source_id", "data_source_id": "<id>"}` and a text block cap of
2000 chars (split into several blocks). The ids live in the consuming
project's CLAUDE.md.
