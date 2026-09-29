## Workflows

A workflow is a script that runs many subagents. The Workflow tool executes it
in the background; the loop, the branching and the intermediate results live in
script variables, and only the final answer reaches your context. With
subagents the plan stays with you, turn by turn, and every result lands in your
context.

### When a Workflow Beats Subagents

Most tasks fit one context and need no independent check: do them yourself, or
hand a few side tasks to subagents. A workflow earns its tokens when one of
these holds:

- **A list too long for one context** — many files, sources, claims or call
  sites, each given the same treatment. A script treats the last item like the
  first; a long conversation does not.
- **A check that must not be skipped** — findings worth reporting only once
  independent agents failed to refute them. In a script the verification runs
  because the code says so, not because someone remembered.
- **A wide solution space** — a hard design or plan, where several independent
  attempts judged against each other beat one attempt iterated.
- **Discovery of unknown size** — bugs, dead code, flaky tests: search in rounds
  until two in a row find nothing new.
- **A fix loop against a gate** — run a check, fix what fails, repeat until it
  passes or stops making progress.

Not for tightly coupled work — edits in sequence, each depending on the last
and on your judgment between them. Multi-agent systems do worst where every
agent needs the same context.

### Propose, Never Launch Unasked

The Workflow tool needs the user's explicit opt-in, and this file is not one:
your job is to **notice and propose**. When the test above holds, say so in one
or two lines — what fans out, what verifies, what synthesizes, roughly how many
agents, and the cost against doing it without one — and run it on a yes. When
the work list is not known yet, scout inline first: the offer is only concrete
once you know what the script would iterate over.

Offer only when the test holds. An offer on every task is noise the user learns
to ignore.

Worth reminding the user of when they fit: the keyword `ultracode` in a prompt
runs that task as a workflow, `/deep-research` is the bundled cross-checked
research workflow, and a run worth repeating can be saved from `/workflows` as
a `/<name>` command.

### Cost

A workflow spends many times the tokens of the same task done inline. Before a
large run, offer to try it on a slice — one directory, one narrow question —
and scale once the slice shows it pays. Model and effort for each `agent()`
call follow `subagent-models.md`.
