## Knowledge Graph (graphify)

Applies only when the project carries a knowledge graph — `graphify-out/graph.json`
exists at the session root. Without it this fragment is inert.

### Query the graph before grepping

- For codebase questions, run `graphify query "<question>"` first. Trace how two
  things connect with `graphify path "<A>" "<B>"`; get a focused view of one
  concept with `graphify explain "<concept>"`. Each returns a scoped subgraph,
  usually far smaller than GRAPH_REPORT.md or raw grep output.
- If `graphify-out/wiki/index.md` exists, use it for broad navigation instead of
  raw source browsing.
- Read `graphify-out/GRAPH_REPORT.md` only for a broad architecture review, or
  when query/path/explain do not surface enough context.

### The graph does NOT cover your branch (read this before trusting a query)

The graph mirrors **one checkout of one integration branch** — whatever branch
answers "how does the system work today" (`main` on trunk-based, `develop` on
gitflow). Task worktrees are excluded via `.graphifyignore`: indexing them would
create twin nodes. So the moment you branch, every file **your branch touches**
becomes a lie the graph tells confidently, with no error raised. Two rules follow,
and they **override the query-first rule above**:

- **Invalidate what you changed.** The exact list is
  `git -C <worktree> diff --name-status origin/<integration-branch>`. For those
  files, read the worktree — not the graph, not a grep of the canonical checkout.
  Everything outside that diff is still trustworthy, which is most of the code.
- **Re-root every path.** Node `source_file` values are relative to the graph
  root (the canonical checkout). Following one verbatim opens the **wrong
  checkout** — the one a task worktree exists precisely to protect. Always
  prefix graph paths with your worktree before reading or editing.

The graph is at its most reliable *before* the worktree exists — during
brainstorm, spec and plan, when the code you reason about is exactly the code it
maps. Its authority decays as the branch grows.

### Keep the graph current

- **Refresh on merge, never while coding.** Right after a merge lands on the
  integration branch: `git pull` the canonical checkout **first** — otherwise
  `graphify update .` faithfully indexes stale code — then run it. Because
  worktrees are excluded, an update run mid-implementation is a no-op by design:
  there is no moment during implementation when updating makes sense.
- **Two rhythms, two costs.** `graphify update .` is AST-only, local and free
  (seconds): run it at every merge — it keeps the *structure* true. But it
  re-partitions the graph, and re-split communities lose their LLM names, falling
  back to hub names (`HealthHandler`, `.Edges`). `label --missing-only` will NOT
  recover them: it sees a name and skips. Only a full `graphify label .` restores
  *readability*, and it costs an LLM pass — so run it periodically (a release is a
  natural trigger), not per merge. With no API key in the environment, name the
  backend explicitly (e.g. `--backend claude-cli`).
- **Sessions must start where `graphify-out/` lives** (the repo or workspace
  root): the graph, its hooks, and `graphify update` all resolve relative to
  the session's cwd.

### Command traps (they fail silently)

- `cluster-only` does **not** re-name with the LLM — it reuses saved labels and
  falls back to hub names. Only `label` calls the model.
- After tightening `.graphifyignore`, `update --force` **keeps** the newly
  excluded nodes (a fail-closed guard). Only `extract` purges them.
- A degraded run still prints a confident summary. Verify the outcome rather than
  trusting `Done — N communities`: count the placeholders and hub names yourself.
