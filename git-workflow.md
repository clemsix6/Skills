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
2. The body states the goal, links the spec and plan under `docs/superpowers/`,
   and summarizes the current state.
3. After every push, update the PR body to reflect the current state.
4. When the work is complete and CI is green, mark the PR ready for review.

### Working on the right code (CRUCIAL)

- Any analysis, investigation, or bug fix starts by checking the branch: be on
  the repo's default branch (`main`, `master`, or `dev` — whatever the repo
  uses) and up to date (`git pull`) before reading the code, unless the task
  explicitly targets another branch. Analyzing a stale or random checkout
  produces conclusions about code that no longer exists.
- When looking for a branch, `git fetch origin` first — the local clone does
  not have every remote branch, and branch listings without a fresh fetch lie.
