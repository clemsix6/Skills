## Subagent Models

Which model and which effort every subagent gets — dispatched through the Agent
tool, a workflow script or a team, inside a pipeline or not.

### Never Fable Unless Asked (CRUCIAL)

**Never dispatch a subagent on Fable unless the user explicitly asks for it.**
Explicit means the user names Fable for the work at hand: a hard task, or this
session running on Fable, is not a request.

- **Set `model` on every dispatch** whose agent definition does not pin one,
  every `agent()` call of a workflow script included. The built-in agents, a
  definition without `model` and a workflow agent without one all take the
  session's model, so on a Fable session they silently become Fable subagents.
- **No fork from a Fable session** — a fork always runs on its parent's model
  and ignores `model`. Dispatch a fresh agent with a written brief instead.

### Model: Does the Work Need Judgment?

Before dispatching, ask whether you can hand the agent **an exact brief and a
way to check its result**.

- **Yes → `sonnet`.** Well-scoped work is what it is built for, faster and
  cheaper than Opus.
- **No → `opus`** — or think it through yourself until you can write both.
  Deciding what to do is judgment, and judgment is what the stronger model
  buys: more effort makes an agent more thorough, never better at choosing the
  approach.

| Work | Model |
|---|---|
| Search, exploration, reading to answer a precise question | `sonnet` |
| Running commands, gathering data, mechanical edits | `sonnet` |
| Implementing a decided change or a planned batch | `sonnet` |
| Drafting a document, a report, a deck | `sonnet` |
| Debugging, the root cause of an unexplained failure | `opus` |
| Code review, checking work against its spec | `opus` |
| Planning, design, arbitrating between options | `opus` |
| Long autonomous work whose approach is not given | `opus` |
| High-volume mechanical work checked right after — driving a browser, bulk extraction | `haiku` |

**Two failures on the same task move it to `opus`.** Two misses on a clear
brief point to the approach, which the stronger model fixes and a third
attempt does not.

### Effort

Effort sets how far an agent verifies its work and chases edge cases. A
workflow script sets it per call (`effort` on `agent()`). **The Agent tool has
no effort parameter**: there it comes from the definition's frontmatter, and an
agent whose definition pins none, built-ins included, runs at this session's
effort. Prefer a definition that pins both when one fits the work: `implement`
(`sonnet`, `medium`) for a decided change.

When choosing an effort — per workflow call, or through the definition you
dispatch:

- **`low`** — rarely for a subagent. No user is there to catch what it skips,
  and Sonnet at `low` sometimes reports a change done without running the
  check that exercises it.
- **`medium`** — well-specified implementation, search, routine commands.
- **`high`** — debugging, review, a bug in existing code, anything with edge
  cases. The starting point for judgment work.
- **`xhigh`** — work full of hidden edge cases, where a missed one ships a
  bug: security-sensitive code, concurrency, parsers and sanitizers, data
  migrations, the review of a large or risky change. On Opus it sits between
  `high` and `max` in both cost and catch.
- **`max`** — only where nothing may be missed: the last review gate before a
  change ships, an exhaustive bug hunt.

On Sonnet, `xhigh` and `max` spend the speed it was picked for, so such work
goes to Opus — except an exhaustive bug hunt with no time pressure, where Sonnet
at `max` found the most bugs of any model measured, at several times Opus's time
and cost.
