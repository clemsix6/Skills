## Git Workflow

`main` is the only long-lived branch. Never push to `main` directly — all work
goes through a short-lived branch and a PR.

### Branching

- Before starting any task: `git checkout main && git pull` — read the code and
  branch from an up-to-date `main`.
- One branch per task, named `type/kebab-description` where `type` is one of
  `feat | fix | refactor | chore | docs | perf`.
- Squash-merge the PR, then delete the branch.

### PR lifecycle (open early, keep current)

1. After the first commit + push, open a **draft** PR. (A PR cannot be opened
   with zero commits, so the first push is the trigger.)
2. The body follows this structure — the first two sections always, the rest
   only when they apply (drop the ones that don't):
   - **Why** — the problem or goal, in 1-3 sentences.
   - **Changes** — `[+]` added · `[&]` changed · `[!]` fixed · `[-]` removed.
   - **Docs** — *when the task has a spec/plan*: links to them under
     `docs/superpowers/` (a feature does; a fix may not).
   - **State** — *when there is a plan*: a checklist mirroring the plan's
     batches (or the work's steps), each item ticked once its commit is pushed,
     unchecked while pending — this is what makes progress readable at a glance.
   - **Deployment notes** — *when relevant*: new env var, secret, migration, or
     service order.
   - **Known issues** — *when applicable*: bugs found but deliberately left
     unfixed as out of scope.
   - **Related PRs** — *when cross-repo*: e.g. requires Entities #9.
3. After every push, update the PR body: tick the batch that just landed and
   refresh any section that moved.
4. When the work is complete and CI is green, mark the PR ready for review.

### Working on the right code (CRUCIAL)

- Any analysis, investigation, or bug fix starts by checking the branch: be on
  the repo's default branch (`main`, `master`, or `dev` — whatever the repo
  uses) and up to date (`git pull`) before reading the code, unless the task
  explicitly targets another branch. Analyzing a stale or random checkout
  produces conclusions about code that no longer exists.
- When looking for a branch, `git fetch origin` first — the local clone does
  not have every remote branch, and branch listings without a fresh fetch lie.
