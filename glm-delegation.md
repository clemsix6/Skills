# Two-tier session

This session runs on two models: this thread on the strong one, the `sonnet`
tier on a lighter model — three times cheaper, same context window.

**This thread reads, diagnoses, plans, decides and reviews. It does not write
code.**

- Once a change is decided, dispatch the `implement` subagent (Agent tool,
  `subagent_type: "implement"`) with the exact change, the files, and the
  verification commands it must run. It edits, verifies, and returns the list
  of files it changed with the outputs.
- Read what comes back as a colleague's diff: check it against what you
  decided, run `git diff` yourself when it matters, send it back with a
  precise note when it is off. You commit; it never does.
- Several independent changes → several `implement` dispatches in one message;
  they run in parallel.
- Prose stays yours: specs, plans, briefs, reports, Markdown of any kind.
- The feature pipeline already works this way through `pipeline-implement`;
  this rule covers everything outside it — fixes, debugging, small changes,
  experiments.
- A hook enforces it: an Edit or Write on a code file from this thread is
  refused with this same instruction. Do not route around it through the shell
  — a `sed` or a heredoc is still you writing code.
