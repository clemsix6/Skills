## Git Workflow

`main` is the only long-lived branch. Never push to `main` directly — every
change goes through a short-lived branch and a PR.

### Branching

- Before starting any task, work from an up-to-date `main`: `git fetch origin`,
  then branch from `origin/main`. Prefer that over `checkout main && pull` when
  other sessions may share the checkout — fetching moves no local ref, so it
  cannot pull the ground out from under them.
- One branch per task, named `type/kebab-description` where `type` is one of
  `feat | fix | refactor | chore | docs | perf`.
- Squash-merge the PR, then delete the branch. Granular commits serve the
  branch's life, not `main`'s history.

### PR lifecycle (open early, keep current)

1. After the first commit + push, open a **draft** PR. (A PR cannot be opened
   with zero commits, so the first push is the trigger.)
2. The body follows this structure — the first two sections always, the rest
   only when they apply (drop the ones that don't):
   - **Why** — the problem or goal, in 1-3 sentences.
   - **Changes** — `[+]` added · `[&]` changed · `[!]` fixed · `[-]` removed.
   - **Docs** — *when the task has a spec/plan*: links to them under
     `docs/superpowers/` (a feature does; a fix may not), plus the SHA of the
     commit holding the spec as approved — the baseline drift is measured
     against, since the file itself moves.
   - **State** — *when there is a plan*: a checklist mirroring the plan's
     batches (or the work's steps), each item ticked once its commit is pushed,
     unchecked while pending — this is what makes progress readable at a glance.
   - **Deployment notes** — *when relevant*: new env var, secret, migration, or
     service order. Assembled from what the work reported, not read off the diff.
   - **Spec adjustments** — *when the spec was changed mid-implementation*: one
     line per change, before → after. Adjusting the spec autonomously is
     allowed; hiding it is not.
   - **Known issues** — *when applicable*: bugs found but deliberately left
     unfixed as out of scope.
   - **Related PRs** — *when cross-repo*: the PRs this one requires or unblocks,
     as `owner/repo#number`.
3. After every push, update the PR body: tick the item that just landed and
   refresh any section that moved. **Only the session that owns the PR writes the
   body** — editing it replaces the whole document, so a second writer building on
   a stale copy erases whatever landed in between. When work is delegated, agents
   report and the owner writes.
4. When the work is complete and CI is green, mark the PR ready for review.

### Working on the right code (CRUCIAL)

- Any analysis, investigation, or bug fix starts by checking the branch: be on
  the repo's default branch (`main`, `master`, or `dev` — whatever the repo
  uses) and up to date (`git pull`) before reading the code, unless the task
  explicitly targets another branch. Analyzing a stale or random checkout
  produces conclusions about code that no longer exists.
- **This does not apply inside a task worktree** — being handed one *is* being
  pointed at another branch. Never run `checkout` or `pull` there: siblings are
  working in that tree, and moving `HEAD` under them destroys their work.
- When looking for a branch, `git fetch origin` first — the local clone does
  not have every remote branch, and branch listings without a fresh fetch lie.
