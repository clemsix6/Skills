# CLAUDE.md

This repository holds shared engineering standards consumed by other projects
through CLAUDE.md `@` imports (see README.md).

## Editing rules

- All content in English.
- Fragments stay **project-agnostic**: no project names, no Notion IDs, no
  hosts, no URLs of internal systems, no credentials. Anything specific belongs
  in the consuming project's CLAUDE.md.
- One fragment = one theme. New cross-cutting defaults go to `general.md`;
  a new language gets its own `<lang>-style.md`.
- Every change lands on `main` and propagates to every machine at the next
  session start — treat each edit as immediately live everywhere.

@~/Skills/commit-convention.md
