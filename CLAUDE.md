# CLAUDE.md

This file provides global guidance to Claude Code when working on Rust repositories.
It describes philosophy and principles — the **why** behind each rule matters more than
the letter. When a situation isn't covered, reason from the why.

## Rust Coding Standards

### KISS Principles (CRUCIAL)

It is CRUCIAL to avoid over-engineering at all costs. Keep everything simple: the
simplest code that compiles and works is usually the best code. Do not create
unnecessary or premature abstractions, do not add features "just in case", prefer
explicit and straightforward code over "clever" code.

**Why this matters MORE in Rust than in Go**: Rust's type system rewards abstraction,
so the temptation to over-engineer is stronger — and the cost is higher. Generics,
trait bounds, and lifetimes don't stay local: they propagate through every signature
that touches them, so each unnecessary one makes the next rewrite more expensive.
Concretely:

- Start with concrete types. Introduce a generic only when a second concrete use
  actually exists — at that point the right abstraction is obvious; before, it's a guess.
- A trait is an interface contract, not a decoration. Write one only for a real seam:
  two implementations that exist today, or a boundary you genuinely need to fake in tests.
- When the borrow checker resists, that is a design signal, not an obstacle to defeat.
  Restructure ownership instead of reaching for `Rc<RefCell<T>>` or lifetime gymnastics.
- `.clone()` is acceptable when it keeps code simple. A clear copy beats a lifetime-heavy
  API; optimize only with profiling evidence, because simplicity lost is rarely regained.
- Do not write macros. Macros are code that writes code — the hardest kind to read and
  debug. Duplication must be severe and purely mechanical before a macro pays for itself.

### Rewrite Over Patch (CRUCIAL)

When the design no longer fits, rewrite the code. Technical debt does not come from
changing a wrong design — it comes from patching around it: adapters, compatibility
shims, deprecated aliases, a `v2` function living next to the `v1` it replaces. None
of that is welcome here. Change the API, update every caller in the same change, and
delete the old path entirely.

Rust is uniquely suited to this ("fearless refactoring"): strong types and exhaustive
matching mean the compiler lists every call site a change breaks — follow the errors
until it compiles, and the rewrite is done. Nothing in this codebase is frozen;
backwards compatibility is a concern for published libraries with external consumers,
not for our own code.

### Minimal Public API (CRUCIAL)

Everything is private by default in Rust — keep it that way. The goal is not to freeze
public items — see "Rewrite Over Patch": nothing is frozen. The goal is cost: every
`pub` multiplies the call sites a rewrite must carry along. A small public surface is
what keeps rewrites cheap — it enables the rewrite culture, it is not a barrier to it.

- `pub(crate)` for items shared inside the crate; plain `pub` only at the deliberate
  API boundary, and each one must answer: "Is this really needed by external code?"
- `lib.rs` is a curated façade: `pub use` the few items consumers actually need, so the
  module tree can be reorganized without breaking anyone.
- A crate with 3 well-designed public functions is better than one with 15 "convenient" ones.

### Documentation

Every item — function, type, field, module — carries a doc comment, private included.
The reason is not bureaucracy: **writing the one-sentence summary is the design test**.
If a function can't be summarized in one sentence, it has more than one responsibility
and must be split. Documentation failure is a design smell detector.

- `///` on items and fields; a short `//!` at the top of each module stating its single
  responsibility (this doubles as the module's reason to exist — if you can't state it,
  the module boundary is wrong).
- Public functions returning `Result` get a `# Errors` section: the caller decides what
  to do with failures, so failures are part of the contract.
- Doc examples on key public APIs are executable (doc-tests) — they are the only form of
  documentation that cannot rot.
- All code and documentation in English.

### Small Units (CRUCIAL)

Good code reads like a story: the main function orchestrates, sub-functions execute
specific tasks, and each file covers one theme. Maximize readability: descriptive
variable and function names, generous spacing between logical blocks — rustfmt and the
compiler already enforce layout and case conventions, so spend the attention on
choosing good names. Size limits are symptoms, not targets — a 40-line function almost
always hides two responsibilities; a 500-line file almost always hides two modules.

- Functions: aim for 15-25 lines; past 30, look for the hidden second responsibility;
  50+ is never acceptable. Note that `?` makes Rust far denser than Go (no three-line
  error checks), so 25 Rust lines already hold a lot of logic. Count logic, not
  ceremony: a signature rustfmt breaks over four lines, or an exhaustive `match` with
  one thin arm per variant (extract any fat arm bodies), is not complexity.
- Files: aim for 200-300 lines of implementation; past 400, split by logical domain.
  The `#[cfg(test)] mod tests` block does NOT count toward the limit — tests are
  mandatory colocated code (see Tests), and counting them would punish thorough
  testing. Exception: a single cohesive type with tightly coupled methods may exceed
  the limit when splitting would scatter related logic and hurt readability — the goal
  is readability, not the number.
- Split the moment a unit grows past its limit or gains a second responsibility —
  never "later". Later never comes, and the next feature builds on the bloat.

### Structure & Growth (CRUCIAL)

The structure must never become the bottleneck of the project. The strategy: keep
boundaries so clean that any reorganization stays cheap.

- Binaries are thin shells: `main.rs` parses configuration, calls into the library,
  maps the top-level error to an exit code. ALL logic lives in library modules — a thin
  binary is the difference between testable and untestable code.
- Start with ONE crate. Split into a Cargo workspace only when a real boundary appears
  (independent reuse, a clear layer, compile-time pain) — premature workspace splits are
  over-engineering like any other.
- Treat every module as a future crate: no cyclic dependencies between modules, ever.
  Rust forbids cycles between crates, so a cycle between modules is precisely the debt
  that will block tomorrow's split.
- Module layout: `foo.rs` with submodules in `foo/` — never `mod.rs` (uniform names
  make navigation predictable).

### Error Handling (CRUCIAL)

An error that reaches a human must tell the story of what the program was trying to do,
layer by layer. A raw low-level error ("connection refused") without that story makes
debugging guesswork — this is the same philosophy as Go's mandatory error wrapping.

- `?` propagates, but never let an error cross an abstraction boundary without context
  describing the operation that failed.
- **Application code**: `anyhow::Result` with `.context(...)` — the caller is a human
  reading a log, so the chain of context IS the product.
- **Library code**: explicit `thiserror` enums preserving the cause via `#[source]` —
  the caller is code that needs to match on failure kinds, so errors are a typed API.
- `.unwrap()` is FORBIDDEN in production code: it asserts "this cannot fail" without
  proof, and turns a recoverable error into a crash. `.expect("...")` is the proven
  version — the message states the invariant that makes failure impossible. Both are
  fine in tests, where a panic is exactly the right failure mode.
- No `_` catch-all when matching enums you own: exhaustive matching is how the compiler
  finds every call site when a variant is added. A `_` silently opts out of that safety.
- Never discard an error silently; `panic!`/`todo!`/`unimplemented!` never ship.

### Ownership & API Design

Default shapes that keep APIs simple and callers free:

- Accept borrows, return owned (`&str` in, `String` out): borrowing inputs costs the
  caller nothing; owning outputs frees the caller from your internal lifetimes.
- No lifetime parameters on public structs until proven necessary — store owned data.
  A lifetime on a struct infects every user of that struct.
- Newtypes for domain identifiers (`struct UserId(i64)`): they cost nothing at runtime
  and turn "passed the wrong id" from a production bug into a compile error.
- Derive `Debug` on every type — you cannot debug or log what you cannot print. Other
  derives (`Clone`, `PartialEq`, serde) only when actually needed: minimal API applies
  to derives too.

### Safety & Enforcement (CRUCIAL)

Rust's whole value proposition is that guarantees come from the compiler, not from
discipline. Extend that principle to the style itself: encode the rules as lints so
they are enforced mechanically, not remembered.

- `#![forbid(unsafe_code)]` in every crate root — one `unsafe` block silently voids the
  memory-safety guarantee for the whole program. Exceptions require explicit human
  approval and a `// SAFETY:` proof comment.
- Each repo carries a `[lints]` table (workspace-level when applicable) turning this
  document into compile errors: `missing_docs`, `clippy::all` + `pedantic`,
  `clippy::missing_docs_in_private_items`, `clippy::unwrap_used` (with
  `allow-unwrap-in-tests = true` in `clippy.toml`).
- Zero-warning policy: `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`
  and `cargo test` pass before any commit.
- Silencing a lint takes a scoped `#[allow]` on the smallest item with a comment saying
  why — a crate-wide allow deletes the rule for everyone, forever.
- rustfmt with DEFAULT configuration: in Rust, formatting is a solved problem — any
  override reopens a debate the ecosystem already closed.
- Always the latest stable toolchain, `edition = "2024"`, `Cargo.lock` committed.
  Never nightly: stability guarantees only exist on stable.

### Dependencies (CRUCIAL)

Every dependency is code you now maintain without controlling. Question each one:
std first, then mainstream well-maintained crates (serde, thiserror, anyhow, tokio,
tracing, clap, reqwest). Adding a crate to save 10 lines is over-engineering.

- It is FORBIDDEN to commit `[patch]` sections, git dependencies, or `path` dependencies
  pointing outside the workspace — local development conveniences, like Go `replace`
  directives, must never reach the repository.

### Tests

- Unit tests live in `#[cfg(test)] mod tests` at the bottom of the file they test —
  colocation keeps them honest when the code changes. Integration tests live in `tests/`.
- Test names describe the behavior, not the function: `rejects_negative_amounts()`
  reads as a spec.
- Async only when the project actually does concurrent I/O; tokio as the single
  runtime; never block inside async code (it starves the whole runtime, not just the
  current task).

### TODO Comments

- Use `// TODO: description` to mark incomplete implementations or future improvements —
  it prevents doing everything at once and prevents forgetting.
- The `todo!()` macro is not a TODO comment: it panics at runtime and must not ship.

### Example Documentation Style

```rust
//! User account management: creation and lookup.

/// A user account in the system.
///
/// Contains authentication and profile information.
#[derive(Debug, Clone)]
pub struct User {
    /// Unique identifier for the user.
    pub id: i64,
    /// Email address used for authentication.
    pub email: String,
}

/// Creates a new user in the database.
///
/// Validates the input and returns the created user with its generated id.
///
/// # Errors
///
/// Returns [`CreateUserError::InvalidEmail`] if the email fails validation,
/// or [`CreateUserError::Insert`] if the database insert fails.
pub async fn create_user(pool: &PgPool, input: CreateUserInput) -> Result<User, CreateUserError> {
    // ...
}
```

### CLAUDE.md Design (CRUCIAL)

- CLAUDE.md files describe the **why** and **principles** — not the exact file tree or crate list
- Do NOT put architecture diagrams with exact directory listings — they become stale after every refactor
- Describe architecture style and rules, not the current structure
- The code is its own documentation for structure — CLAUDE.md captures what is NOT visible in the code
- A good CLAUDE.md should rarely need updating; if it changes every commit, it's too specific
