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

### Model: Haiku Reads, Sonnet Builds, Opus Judges

Before dispatching, ask whether you can hand the agent **an exact brief and a
way to check its result**.

- **No → `opus`** — or think it through yourself until you can write both.
  Deciding what to do is judgment, and judgment is what the stronger model
  buys: more effort makes an agent more thorough, never better at choosing the
  approach.
- **Yes, and the agent changes something** — code, a file, a document →
  `sonnet`. Well-scoped work is what it is built for, faster and cheaper than
  Opus.
- **Yes, and the agent only reads, runs and reports → `haiku`**, provided a
  wrong or incomplete answer would show when you use it.

| Work | Model |
|---|---|
| A lookup — where something is defined, which code handles a case, one precise question | `haiku` |
| Running commands and reporting what they print — tests, builds, logs, queries | `haiku` |
| Fetching documentation or web pages and condensing them | `haiku` |
| Bulk extraction or classification; a workflow's fan-out readers, one per item | `haiku` |
| Driving a browser | `haiku` |
| Exploration you will build on without re-reading — how a subsystem works, what a change touches | `sonnet` |
| Mechanical edits, implementing a decided change or a planned batch | `sonnet` |
| Drafting a document, a report, a deck | `sonnet` |
| Debugging, the root cause of an unexplained failure | `opus` |
| Code review, checking work against its spec | `opus` |
| Planning, design, arbitrating between options | `opus` |
| Long autonomous work whose approach is not given | `opus` |

**Misses move a task up.** A Haiku answer that proves wrong or incomplete sends
the task to `sonnet`: the miss shows the task was not as narrow as it looked.
Two failures by Sonnet on the same task move it to `opus` — two misses on a
clear brief point to the approach, which the stronger model fixes and a third
attempt does not.

### Haiku: Nearly Free, Fastest, Narrow

Haiku costs a small fraction of Sonnet — on a subscription it barely registers
against the plan's limits — and it is the fastest model. So the question is
never whether a task is worth a Haiku agent, only whether the task is narrow:

- **Narrow work holds up.** Lookups, extraction, summaries, classification,
  driving a browser or a desktop: there it reaches most of Sonnet's level.
- **Long multi-step coding does not** — there it scores about half of what
  Sonnet does. Anthropic places it as a subagent under a Sonnet or Opus lead,
  not as the agent that writes the change.
- **Its misses are quiet.** At low effort or under a long brief it can skip a
  search, stop before the work is done, or call a change done without running
  the check. Hence read-and-report work only, and a report you can check at a
  glance: **ask for evidence, not verdicts** — the path and line found, the
  failing output quoted, the figure with its source.

Being nearly free, it also moves the point where delegating pays: a search or a
command whose raw output would flood your context costs next to nothing on
Haiku, and only the answer comes back.

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

On Haiku, `medium` — its default — fits nearly everything it should get;
`high` when the brief carries a long list of rules or a strict output format.
Never `low`: that is where it skips searches and stops early. Work that seems
to need more than `high` is not narrow — give it to Sonnet. From the Agent
tool Haiku runs at the session's effort, which is fine: above `high` it gets
slower, still for next to nothing.
