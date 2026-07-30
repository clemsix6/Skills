## Heavy execution

Picked by the supervisor at step 2 of `feature-pipeline.md`, which everything
here continues. The batch is the unit of review and push.

4. **Spec** — standard, in `<worktree>/docs/superpowers/specs/`.
5. **Spec review** — dispatch `pipeline-spec-review`. The brainstorm is a
   conversation, not a file: restate its intent in the prompt.
6. **Fix the spec** — apply the feedback. If a fix changes what the feature does
   for its user, re-run step 5: the supervisor is about to approve this document.
   Two rounds at most, then take it to them as it stands.
7. **Spec summary to the supervisor** — include every item the review marked
   user-visible, from all rounds. The only point where a human approves the work,
   and the one that seals the scope.
8. **Commit the approved spec, push, open the draft PR** — record that commit's
   SHA in the PR body under `Docs`. It is the baseline the final review measures
   drift against.
9. **Plan** — see "Plan rules", in `<worktree>/docs/superpowers/plans/`, plus the
   parallelism rules below.
10. **Plan review** — dispatch `pipeline-plan-review`. The only pass that sees
    the plan whole, so cross-batch coherence and coverage are caught here or
    nowhere.
11. **Fix the plan, commit and push it** — whether or not it changed, so the PR's
    `Docs` link resolves. Add the `State` checklist to the PR body, one line per
    batch. Re-run step 10 if the fix re-batches or changes an annotation. Two
    rounds at most, then stop and ask the supervisor: a plan rejected twice is
    answering a problem in the spec.
12. **Implementation** — dispatch one `pipeline-batch-manager` per batch, in plan
    order, one at a time. Push your own commits before dispatching, since a
    blocked batch is undone by rewinding to the remote.

    Each batch returns **clean** or **blocked**. On clean, tick it in `State` and
    move on. On blocked: rewind the branch to the remote, fix what the synthesis
    reports, commit and push the plan, and re-dispatch — telling the new
    batch-manager what blocked the last attempt. **Two attempts per batch**, then
    stop and report.
13. **Final review** — dispatch `pipeline-final-review`. It tags findings `fix`
    or `supervisor`: apply the first, take the second to the supervisor. Commit
    and push those fixes, **then** dispatch it again — it reads a committed diff,
    so uncommitted work is invisible to it. That second verdict is final; never
    grade your own fix. If it fails, stop and report rather than marking the PR
    ready. If it passes, mark ready once CI is green.

### Parallelism (heavy only)

A batch's tasks are implemented by several agents at once, so the plan has to say
which may run together.

- **Mark each task `same-agent` or `parallel`.** Parallel tasks get one agent
  each; `same-agent` tasks share one, because the accumulated context is what
  keeps their design decisions consistent. Two tasks are only parallel if they
  share no file **and no compilation unit** — no Go package, no Rust crate, no
  module the toolchain builds as a whole. Agents building the same unit compile
  each other's half-written work.
- **Implementation tasks never touch the composition root**: it is one file, so
  tasks that each wired themselves could never be parallel. That wiring is the
  batch's integration task, dispatched alone after the others.

### Work that surfaces between batches

A batch-manager reports plan findings rather than fixing them, because only you
see the batches after it. When one turns out to be missing work, it goes into the
batch whose scope it belongs to — not a fix batch appended at the end, which
every batch in between would have built on top of.
