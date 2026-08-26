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
2. **Workspace + branch** — create the worktree (see "Task workspace").
   Everything after this — spec, plan, code, commits — lives inside it.
3. **Spec** — standard, in `<worktree>/docs/superpowers/specs/`. It is not
   reviewed on its own; the review at step 7 covers it.
4. **Spec summary to the supervisor** — the only point where a human approves the
   work, and the one that seals the scope. Nothing is built until they accept it.
5. **Commit the approved spec, push, open the draft PR** — record that commit's
   SHA in the PR body under `Docs`. It is the baseline the final review measures
   drift against.
6. **Plan** — see "Plan rules", in `<worktree>/docs/superpowers/plans/`. Batched
   as usual: a batch goes to one agent whole. **The execution handoff at the end
   of `writing-plans` is already answered** — step 9 is this pipeline's subagent
   execution. Never put that choice to the supervisor, and never hand over to
   `executing-plans` or `subagent-driven-development`: SDD's per-task loop,
   ledger and review protocol would replace steps 9-10 wholesale.
7. **Spec and plan review** — dispatch `pipeline-spec-plan-review`, on the two
   documents together. The only pass before code exists.
8. **Fix the plan, commit and push it** — whether or not it changed, so the PR's
   `Docs` link resolves. Add the `State` checklist to the PR body, one line per
   batch. A finding against the **spec** cannot be fixed here — the supervisor
   sealed it at step 4, so take it back to them.
9. **Implementation** — dispatch `pipeline-implement` once per batch, in plan
   order, **one batch at a time**, giving it the whole batch including the
   integration task. Pass `model: opus` for a batch containing a task the plan
   marks complex. When the batch comes back clean: push every commit it
   produced, tick it in `State`, then dispatch the next one.

   **A blocked batch is yours to unblock.** Whether it reports a defect in the
   plan or a task impossible as specified, both are the plan, and the plan is
   yours: rule on it, fix it, commit and push it, rewind the branch to the
   remote, and re-dispatch the batch — telling the new agent what blocked the
   last attempt. **Three attempts per batch**, the third on `model: opus`.

   The rewind is what makes that safe: every earlier batch is already pushed, so
   the remote is the last clean boundary, and the commits the blocked attempt
   produced were written against a plan that no longer says the same thing.

   Take it to the supervisor only when the fix would change what the end user
   gets — that is the spec, and they sealed it — or when three attempts came back
   blocked, or when every path forward is a guess. "It is a judgment call" is not
   one of those: make the call, and let the plan commit record it.

   An agent that **dies mid-batch** (stall, API error) is not a blocked batch: do
   not rewind, do not redo. The worktree is the ground truth — `git log
   origin/main..HEAD` and `git status` say which tasks landed and what remains.
   Re-dispatch the remainder with that state spelled out. This recovery is what
   1 task = 1 commit buys; protect it by forbidding amend and rebase in every
   dispatch.
10. **Final review** — dispatch `pipeline-final-review`. It tags findings `fix`
    or `supervisor`: apply the first, take the second to the supervisor. Commit
    and push those fixes, **then** dispatch it again — it reads a committed diff,
    so uncommitted work is invisible to it. That second verdict is final; never
    grade your own fix. If it fails, stop and report rather than marking the PR
    ready. If it passes, mark ready once CI is green.

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
- **1 task = 1 commit**, and **a batch ends with every one of them pushed**.
  Exception: an integration task that only verifies (full suite, vet, sweeps)
  commits nothing when everything is green — its artifact is the green gate and
  the updated PR body; it commits only the fixes it surfaces.

### Dispatch

**Every prompt carries the absolute worktree path.** A subagent starts in the
main checkout, so a relative path reads the wrong tree and commits to the wrong
branch. Beyond that, supply what the target definition's "What you are given"
asks for.

Pass **pointers, never content**: which task, where the plan and spec live. An
agent that reads the source itself cannot be handed a lossy summary of it.

### What comes back

**You are the only writer of the spec, the plan and the PR body.** Agents report;
you write. Act on four things:

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

Review on the strong model where the whole feature is at stake, execution on the
cheap one.

| Role | Model | Dispatched as |
|---|---|---|
| Spec + plan review | current | `pipeline-spec-plan-review` |
| Implementation | sonnet | `pipeline-implement`; pass `model: opus` for a batch containing a task the plan marks complex, and for a batch's third attempt |
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
  or force-push.
- **Remove the worktree and the branch after the PR merges.**
