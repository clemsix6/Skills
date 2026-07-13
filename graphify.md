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

### Keep the graph current

- **After modifying code**, run `graphify update .` (AST-only, local, no API
  cost).
- **The graph maps the canonical checkouts.** Task worktrees (`.wt/`) are
  excluded via `.graphifyignore` — indexing them would create twin nodes. The
  graph therefore describes `main`, not the in-flight branch: update after
  merge, not during implementation.
- **Sessions must start where `graphify-out/` lives** (the repo or workspace
  root): the graph, its hooks, and `graphify update` all resolve relative to
  the session's cwd.
