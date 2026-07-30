## Development Workflow

This pipeline is for **adding a feature**: work that gives a user a capability
they did not have. Size is not the test — a one-file change that exposes a new
capability is a feature, a sweeping refactor that exposes none is not. Bugs,
refactors, investigations and ops are done directly, with systematic-debugging
for bugs. When you skip this pipeline, say in one line which side of that test
the work falls on.

The project CLAUDE.md may add steps or override the task-workspace pattern.

### Pipeline (in order)

1. **Brainstorming** — superpowers `brainstorming` skill. Reads the main
   checkout, writes nothing.
2. **Mode** — ask the supervisor: **heavy** or **light**. Settled here, never
   revisited mid-run.

   - **heavy** — the spec and the plan are each reviewed on their own, and every
     batch gets a plan review before it and a diff review after.
   - **light** — one combined spec-and-plan review, one agent per batch, one
     review at the end.

   Recommend one in a sentence — **light when there is nothing left to design** —
   and run **heavy if they pick neither**.
3. **Workspace + branch** — create the worktree (see "Task workspace").
   Everything after this — spec, plan, code, commits — lives inside it.

**Then read `~/Skills/feature-pipeline-heavy.md` or
`~/Skills/feature-pipeline-light.md`**, whichever was picked, and follow it from
step 4. Both end at the same place: the PR marked ready.

### Plan rules (differ from superpowers)

- **Single phase, mandatory** — everything requested is implemented in this
  iteration. A deferred remainder never gets these gates.
- **Batches of ~1-5 tasks**, ordered, run one at a time.
- **Every batch ends with an integration task**, ordered after the others: the
  composition-root lines that make the batch's code reachable, or the tests that
  exercise it when the batch delivers foundations a later batch consumes. Never
  neither — that is what stops a batch landing code nothing reaches. A
  single-task batch carries its own integration.
- **Mark the tasks that need a stronger model** (see "Models"). The plan is where
  the whole picture is visible; deciding it at dispatch time defaults to "not
  complex" every time.
- **1 task = 1 commit**, and **a batch ends with every one of them pushed** — in
  both modes.

### Dispatch

**Every prompt carries the absolute worktree path.** A subagent starts in the
main checkout, so a relative path reads the wrong tree and commits to the wrong
branch. Beyond that, supply what the target definition's "What you are given"
asks for.

Pass **pointers, never content**: which task, where the plan and spec live. An
agent that reads the source itself cannot be handed a lossy summary of it.

### What comes back

**You are the only writer of the spec, the plan and the PR body.** Agents report;
you write. Whatever mode you are in, act on four things:

- **`plan` and `spec` findings** — no agent may write either file. Fix the plan
  yourself and push it before anything else builds on it.
- **As-built divergences** — a name, signature or behaviour that ended up
  different from the plan's prediction. Write them into the plan: nothing else
  carries them, and later work would build on a stale assumption.
- **Deployment impact** — env var, secret, migration, service ordering. It
  reaches the PR through no other path.
- **Anything left unfixed**, and any finding you decide not to act on, goes into
  `Known issues` when you take the decision, not at the end.

### Scope (mandatory)

**The approved spec is the scope.** The supervisor's approval seals it: after
that, nothing is added to what the feature does and nothing about its behaviour
changes — at any stage, by any agent, including you.

Reviews will find real bugs and real inconsistencies that sit outside the spec.
Every one of them is **reported, never fixed.** A correction nobody asked for
ships behaviour nobody approved, inside a PR whose scope its reviewer trusts.
They go to `Known issues` and to the supervisor.

One exception, and its test:

> Does the plan need this fixed to be implementable at all?

**Yes** — fix it, and say so in the PR: a blocker on the path to the spec was
implicitly in scope from the start. **No** — report it, however small and however
obviously right.

### Spec adjustments

You may adjust the spec autonomously. The line:

> Does the change alter what the end user gets?

- **No** — the mechanism turned out impractical, the observable behaviour is the
  one that was validated. Adjust, commit it separately (`[&]`), add a
  `Spec adjustments` entry to the PR body.
- **Yes** — a use case disappears, an output format changes, a guarantee drops,
  scope is added. Ask the supervisor. Once approved, record that commit in `Docs`
  as an **additional** approved revision; never replace the original, or every
  earlier autonomous adjustment silently becomes "approved".

### Models

Reasoning and review on the strong model, execution on the cheap one — most
defects originate in the plan.

| Role | Model | Dispatched as |
|---|---|---|
| Spec review (heavy) | opus | `pipeline-spec-review` |
| Plan review (heavy) | opus | `pipeline-plan-review` |
| Spec + plan review (light) | current | `pipeline-spec-plan-review` |
| Batch-manager (heavy) | opus | `pipeline-batch-manager` |
| Scoped plan review (heavy) | opus | `pipeline-batch-plan-review` |
| Implementation | sonnet | `pipeline-implement`; pass `model: opus` for a task the plan marks complex |
| Batch review (heavy) | opus | `pipeline-batch-review` |
| Final review | opus | `pipeline-final-review` |

This fragment loads into every one of those agents, so it describes the pipeline
from your seat only. **Where any shared fragment and an agent's own definition
could be read as disagreeing, the definition wins.**

### Task workspace

Two sessions must never write the same checkout, so this feature gets a worktree
of its own and **the main checkout is never touched again for this task**.

- **Create it beside the repository, never inside it**: branch from
  `origin/main` into `../<repo>.wt/<task>`. Nested, a parent workspace file
  resolves it against the main checkout and builds there compile the wrong tree
  without complaining.
- **Only you move `HEAD`** — no agent may `checkout`, `pull`, `rebase`, `amend`
  or force-push, which is what makes the post-block rewind safe.
- **Remove the worktree and the branch after the PR merges.**
