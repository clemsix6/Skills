## Development Workflow

This pipeline is for **adding a feature** — building something new. It wraps
review + autonomous-fix gates around the spec and the plan, and changes how the
plan is structured and executed.

**It applies to feature additions ONLY.** Debugging, bug fixes, refactors,
investigations, and ops do NOT follow it — no brainstorm, no spec, no worktree
ceremony. Fix bugs with systematic-debugging (reproduce → diagnose → fix →
verify), make small or contained changes directly, and use judgment. Reserve the
full pipeline below for genuinely new features.

The project CLAUDE.md may insert additional steps or override the task-workspace
pattern — check it before starting the pipeline.

### Pipeline (in order)

1. **Brainstorming** — superpowers `brainstorming` skill (standard).
2. **Spec** — write the spec (standard), in `docs/superpowers/specs/`.
3. **Spec review** — dispatch a subagent to review the spec: is it aligned with
   the brainstorm? Hunt for problems, gaps, and incoherences.
4. **Fix the spec** — apply the review feedback autonomously.
5. **Spec summary to the user** — only once the spec is corrected, send a
   bullet-point summary for the supervisor to validate. This is the single human
   checkpoint of the flow.
6. **Plan** — write the plan (see "Plan rules" below), in `docs/superpowers/plans/`.
7. **Plan + spec review** — dispatch a subagent to review the package; the spec
   matters but the focus is the plan: plan↔spec alignment, overall coherence,
   potential bugs/problems.
8. **Fix the plan** — apply the review feedback autonomously.
9. **Workspace + branch + PR** — as soon as the plan is clean (right after step
   8, before any implementation), create the isolated task workspace (see "Task
   workspace" below), branch, and open the draft PR with the superpowers docs
   inside. Keep the PR body up to date.
10. **Implementation** — chain it directly after the plan. Subagent-driven by
    default; inline only in the rare cases where it is recommended.

### Plan rules (differ from superpowers)

- **Single phase, mandatory** — at the end of the plan's first iteration,
  everything requested in the brainstorm is implemented. No "phase 2 later."
- **Batched tasks** — group the superpowers tasks into batches of ~1-5 so one
  subagent implements a whole batch (saves time and tokens).
- **1 task = 1 commit** — batching never merges commits; the task stays the unit
  of commit and audit.

### Per-batch rules

- **Each batch leaves the build green** — a batch carries its own wiring (the
  composition-root lines that construct the new code and make it reachable), so
  the feature is actually wired and the project's build and vet/lint commands
  pass with it reachable. Never defer all wiring to a final "wiring batch" —
  that leaves intermediate batches as dead, untestable code.
- At the end of a batch, if it is **critical**, run a code review of the batch
  and fix the feedback autonomously. Most of the time this is not needed.
- Then push all the batch's commits.

### Task workspace (autonomous — parallel-session isolation)

Several tasks can run in parallel sessions, but two sessions must never write
the same checkout. Sessions start from the repo root on an up-to-date `main`;
brainstorm, spec and plan all read the main checkout. Right before
implementation, create an isolated worktree so this session is the **sole
writer**, then do ALL implementation inside it. **Once the worktree exists,
never touch the main checkout for this task** — that single rule is what keeps
parallel sessions from colliding.

- **Create**: `git fetch origin`, then
  `git worktree add -b <type>/<task> .wt/<task> origin/main`.
  Branching from `origin/main` leaves the main checkout free for other sessions.
  (`.wt/` is gitignored.)
- **No CWD change** — absolute paths for edits; the `-C` flag for every command
  (`git -C .wt/<task> …`, `go -C .wt/<task> test ./...`).
- **Clean up** at merge: `git worktree remove .wt/<task>`. If the session ends
  before merge, leave it (`git worktree prune` reclaims stale ones later).
