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
3. **Spec** — standard, in `<worktree>/docs/superpowers/specs/`.
4. **Spec review** — dispatch `pipeline-spec-review`. The brainstorm is a
   conversation, not a file: restate its intent in the prompt.
5. **Fix the spec** — apply the feedback. If a fix changes what the feature does
   for its user, re-run step 4: the supervisor is about to approve this document.
   Two rounds at most, then take it to them as it stands.
6. **Spec summary to the supervisor** — include every item the review marked
   user-visible, from all rounds. This is the only planned human checkpoint.
7. **Commit the approved spec, push, open the draft PR** — record that commit's
   SHA in the PR body under `Docs`. It is the baseline the final review measures
   drift against.
8. **Plan** — see "Plan rules", in `<worktree>/docs/superpowers/plans/`.
9. **Plan review** — dispatch `pipeline-plan-review`. The only pass that sees the
   plan whole, so cross-batch coherence and coverage are caught here or nowhere.
10. **Fix the plan, commit and push it** — whether or not it changed, so the PR's
    `Docs` link resolves. Add the `State` checklist to the PR body, one line per
    batch. Re-run step 9 if the fix re-batches or changes an annotation. Two
    rounds at most, then stop and ask the supervisor: a plan rejected twice is
    answering a problem in the spec.
11. **Implementation** — dispatch one `pipeline-batch-manager` per batch, in plan
    order, one at a time. Push your own commits before dispatching, since a
    blocked batch is undone by rewinding to the remote.

    Each batch returns **clean** or **blocked**. On clean, tick it in `State` and
    move on. On blocked: rewind the branch to the remote, fix what the synthesis
    reports, commit and push the plan, and re-dispatch — telling the new
    batch-manager what blocked the last attempt. **Two attempts per batch**, then
    stop and report.
12. **Final review** — dispatch `pipeline-final-review`. It tags findings `fix`
    or `supervisor`: apply the first, take the second to the supervisor. Commit
    and push those fixes, **then** dispatch it again — it reads a committed diff,
    so uncommitted work is invisible to it. That second verdict is final; never
    grade your own fix. If it fails, stop and report rather than marking the PR
    ready. If it passes, mark ready once CI is green.

### Plan rules (differ from superpowers)

- **Single phase, mandatory** — everything requested is implemented in this
  iteration. A deferred remainder never gets these gates.
- **Batches of ~1-5 tasks**, ordered, run one at a time. The batch is the unit of
  review and push, not of implementation.
- **Mark each task `same-agent` or `parallel`.** Parallel tasks get one agent
  each; `same-agent` tasks share one, because the accumulated context is what
  keeps their design decisions consistent. Two tasks are only parallel if they
  share no file **and no compilation unit** — no Go package, no Rust crate, no
  module the toolchain builds as a whole. Agents building the same unit compile
  each other's half-written work.
- **Every batch ends with an integration task**, ordered after the others and
  dispatched alone: the composition-root lines that make the batch's code
  reachable, or the tests that exercise it when the batch delivers foundations a
  later batch consumes. Never neither — that is what stops a batch landing code
  nothing reaches. Implementation tasks never touch the composition root: it is
  one file, so tasks that each wired themselves could never be parallel. A
  single-task batch carries its own integration.
- **Mark the tasks that need a stronger model** (see "Models"). The plan is where
  the whole picture is visible; deciding it at dispatch time defaults to "not
  complex" every time.
- **1 task = 1 commit.**

### Dispatch

**Every prompt carries the absolute worktree path.** A subagent starts in the
main checkout, so a relative path reads the wrong tree and commits to the wrong
branch. Beyond that, supply what the target definition's "What you are given"
asks for.

Pass **pointers, never content**: which task, where the plan and spec live. An
agent that reads the source itself cannot be handed a lossy summary of it.

### What comes back

A batch-manager returns a short synthesis. Act on four things:

- **`plan` and `spec` findings** — it may not write either file, because only you
  see the downstream batches. Fix the plan and push it before the next batch.
  Work that turns out to be missing goes into the batch whose scope it belongs
  to, rather than a fix batch appended at the end that the batches in between
  would build on top of.
- **As-built divergences** — a name, signature or behaviour that ended up
  different from the plan's prediction. Write them into the plan: nothing else
  carries them, and the next batch would build on a stale assumption.
- **Deployment impact** — env var, secret, migration, service ordering. It
  reaches the PR through no other path.
- **Anything left unfixed**, and any finding you decide not to act on, goes into
  `Known issues` when you take the decision, not at the end.

**You are the only writer of the spec, the plan and the PR body.** Agents report;
you write.

### Scope (mandatory)

**The approved spec is the scope.** Step 6 seals it: after that, nothing is added
to what the feature does and nothing about its behaviour changes — at any stage,
by any agent, including you.

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
| Spec review (step 4) | opus | `pipeline-spec-review` |
| Plan review (step 9) | opus | `pipeline-plan-review` |
| Batch-manager | opus | `pipeline-batch-manager` |
| Scoped plan review | opus | `pipeline-batch-plan-review` |
| Implementation | sonnet | `pipeline-implement`; pass `model: opus` for a task the plan marks complex |
| Batch review | opus | `pipeline-batch-review` |
| Final review (step 12) | opus | `pipeline-final-review` |

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
