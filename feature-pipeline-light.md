## Light execution

Picked by the supervisor at step 2 of `feature-pipeline.md`, which everything
here continues.

4. **Spec** — standard, in `<worktree>/docs/superpowers/specs/`. It is not
   reviewed on its own; the review at step 8 covers it.
5. **Spec summary to the supervisor** — the only point where a human approves the
   work, and the one that seals the scope. Nothing is built until they accept it.
6. **Commit the approved spec, push, open the draft PR** — record that commit's
   SHA in the PR body under `Docs`. It is the baseline the final review measures
   drift against.
7. **Plan** — see "Plan rules", in `<worktree>/docs/superpowers/plans/`. Batched
   as usual, with **no `parallel` / `same-agent` annotation**: a batch goes to one
   agent whole.
8. **Spec and plan review** — dispatch `pipeline-spec-plan-review`, on the two
   documents together. The only pass before code exists.
9. **Fix the plan, commit and push it** — whether or not it changed, so the PR's
   `Docs` link resolves. Add the `State` checklist to the PR body, one line per
   batch. A finding against the **spec** cannot be fixed here — the supervisor
   sealed it at step 5, so take it back to them.
10. **Implementation** — dispatch `pipeline-implement` once per batch, in plan
    order, **one batch at a time**, giving it the whole batch including the
    integration task. Pass `model: opus` for a batch containing a task the plan
    marks complex. When the batch comes back: push every commit it produced, tick
    it in `State`, then dispatch the next one.

    A batch that comes back reporting its task impossible, or a defect in the
    plan, goes to the supervisor. No second attempt.
11. **Final review** — dispatch `pipeline-final-review`. It tags findings `fix`
    or `supervisor`: apply the first, take the second to the supervisor. Commit
    and push those fixes, **then** dispatch it again — it reads a committed diff,
    so uncommitted work is invisible to it. That second verdict is final; never
    grade your own fix. If it fails, stop and report rather than marking the PR
    ready. If it passes, mark ready once CI is green.
