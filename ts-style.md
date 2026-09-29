## TypeScript & React Coding Standards

Applies to every TypeScript codebase: React Native / Expo apps, React web apps,
Node scripts. The React and React Native sections apply where those are used.

### KISS Principles (CRUCIAL)

- It is CRUCIAL to avoid over-engineering at all costs
- Keep everything simple: Keep It Simple, Stupid (KISS)
- Do not create unnecessary or premature abstractions
- Prefer explicit and straightforward code over "clever" code
- Do not add features "just in case" - only implement what is actually needed
- Type-level cleverness is over-engineering too: a conditional or mapped type
  nobody can read in one pass costs more than the duplication it removes
- The simplest code that works is often the best code

### Rewrite Over Patch (CRUCIAL)

- When a design no longer fits, change it: update the API and every caller in the
  same change, then delete the old path
- No adapters kept around an old API, no deprecated aliases, no `v2` living next to
  the `v1` it replaces, no commented-out code — git remembers
- Dead code is deleted, not left "in case": an unused export, prop, file or style
  is a lie about what the code needs
- Exception: a contract with code you do not ship together (a released app build,
  another repository) follows that project's compatibility rules

### Typing (CRUCIAL)

The type system is the first reviewer: a type that tells the truth about the domain
turns a whole class of bugs into compile errors.

- `strict: true` and `noUncheckedIndexedAccess` in every `tsconfig.json`
- `any` is FORBIDDEN. Unknown data is `unknown` and gets narrowed before use
- No `as` casts to silence the compiler. A cast is allowed only at a validated
  boundary, with a comment saying what guarantees it. `as const` is fine
- No non-null assertion (`value!`): narrow with a check instead
- No `@ts-ignore`. `@ts-expect-error` only for a third-party typing bug, with the
  reason on the same line
- Make impossible states unrepresentable: a discriminated union
  (`{ status: 'loading' } | { status: 'error'; error: Error } | { status: 'ready'; data: T }`)
  instead of parallel flags (`isLoading`, `isError`, `data?`)
- Every `switch` over a union is exhaustive, ending with a `never` check, so adding a
  variant lists every place that must handle it
- String literal unions (derived from an `as const` array when the values are also
  needed at runtime) instead of `enum`
- External data (API responses, storage, route params, env) is parsed once at the
  boundary into a domain type; the rest of the code never sees the raw shape
- Explicit parameter and return types on exported functions; inference inside
- `type` by default; `interface` only when a type is meant to be extended
- Props, arguments and state are never mutated: return new values
- Generics describe a real relationship between types (`<T>(items: T[]) => T | undefined`),
  never a decoration. A generic parameter used once is a smell

### Reuse & Generic Code (CRUCIAL)

One concept has one implementation. Duplication is how UIs drift apart: two copies
of the same card end up with two paddings, two colors, two bugs.

- When two components or screens differ only by their data or a few values, they
  are ONE component with props. Merge them, even if the merged version changes a
  detail in one of them
- Extract a shared component, hook or function the second time a shape appears —
  not the first (that is a guess) and not the fifth (that is debt)
- A generic component is configured by data and composition, not by flags:
  - a `variant` union (`'primary' | 'secondary' | 'danger'`) instead of
    `isPrimary` / `isDanger` booleans
  - `children` or named slot props instead of a boolean per optional section
  - more than two boolean props on one component means it is two components
- Formatting, parsing and business rules are pure functions shared by every screen
  that needs them, never re-implemented inline in a component

### Minimal Public API (CRUCIAL)

- Export only what another module actually imports; everything else stays
  module-private
- Start with the absolute minimum: if a module needs to expose 2 functions, expose 2
- No barrel files (`index.ts` re-exporting a folder) inside an application: import
  from the module that defines the thing. A barrel drags every dependency of every
  re-exported module into each consumer, tests included
- A package exposes deliberate entry points through its `exports` map — one per
  family of features, so a consumer only loads what it imports
- A component takes the props it needs, nothing "just in case". No blind
  `...rest` forwarding, except in a thin wrapper around a primitive

### Structure (CRUCIAL)

The structure must make the right place for new code obvious, and keep any later
reorganization cheap.

- Layers, with dependencies pointing one way only:
  - **routes / screens** compose: they read the route, call hooks, wire navigation
    and translation, and render feature components. They hold no business logic
  - **feature components** assemble the UI of one domain
  - **presentational components and primitives** render only from their props: no
    data fetching, no global store, no router, no translation lookup — they receive
    already-formatted, already-translated values
  - **hooks** hold stateful UI logic and bind services and stores to components
  - **services** do I/O and return domain types; they never import React
  - **stores** hold only state shared across screens; everything else is local state
- Group code by domain (`wallet/`, `feed/`, `account/`), with shared primitives in
  one place. A folder per technical type (`helpers/`, `misc/`) is where code goes
  to be forgotten
- No cyclic imports between modules, ever
- Each module has one responsibility you can state in one sentence. If you cannot,
  the boundary is wrong

### React Components

- One component per file, the file named after it. A small private subcomponent
  used only there may share the file while the file stays within its size limit
- Props type named `<Component>Props`; optional props get their default in the
  destructuring
- Values derived from props or state are computed during render, never copied into
  state or synchronized by an effect
- `useEffect` only synchronizes with an external system (subscription, timer,
  imperative API), and always returns its cleanup
- Custom hooks: `use` prefix, one responsibility, a typed return value, no JSX
- List keys are stable ids, never the array index of a list that changes
- Memoization (`useMemo`, `useCallback`, `memo`) is not a default. With the React
  Compiler enabled, never memoize by hand; without it, memoize only for a measured
  cost or a referential stability a dependency actually needs

### Styling (CRUCIAL)

- No hardcoded design values: colors, font sizes, font weights, spacing, radii,
  shadows, opacities and durations come from the design tokens
- One scale: every size and spacing is a step of the token scale. A value the
  design really needs and the scale lacks is added to the tokens, never inlined
- Styles are declared once at module level (`StyleSheet.create`, CSS module,
  utility classes) and never built during render
- Variants are predefined styles selected by a prop; an inline style only carries a
  value computed at runtime (a measured size, an animated value)
- Themes go through the theme tokens, never `isDark ? '#fff' : '#000'`

### React Native

- Platform differences live in platform files (`Chart.native.tsx` beside
  `Chart.tsx`), not in `Platform.OS` branches spread through a component
- A native-only module (blur, glass, symbols, haptics) is wrapped once in a
  primitive; the rest of the app imports the primitive, never the module
- Animations and gestures run on the UI thread (Reanimated, Gesture Handler);
  JS-driven animation is not used

### Documentation Requirements

- Every function, component, hook, type and module-level constant has a TSDoc
  comment (`/** ... */`), private ones included
- The first sentence summarizes what it does or represents. Writing it is the design
  test: if it cannot be summarized in one sentence, it does more than one thing and
  must be split
- Every prop and every field of a type is documented with a `/** ... */` comment on
  its own line — the IDE shows it on hover, a `//` comment it does not
- `@param` and `@returns` only when the name and type do not already say it;
  `@throws` whenever throwing is part of the contract
- No file-header banners (file name, author, date): git records them
- All code and documentation must be written in English

### Code Style

- Maximize readability with generous spacing between logical blocks
- Use descriptive names: `walletPerformance`, not `wp` or `data2`
- Naming conventions:
  - PascalCase for components, types and component files
  - camelCase for functions, variables, hooks and non-component files
  - UPPER_SNAKE_CASE for module-level constants whose value never changes
  - booleans read as questions (`isVisible`, `hasSources`)
  - event props are `onX`, their handlers `handleX`
- Early returns over nested conditions; no nested ternaries
- `const` by default, `let` only when the value is reassigned, never `var`
- `??` for defaults (never `||` on values that can legitimately be `0` or `''`),
  `?.` for optional access
- Formatting is the formatter's job: never argue it by hand

### Function Size (CRUCIAL)

- Functions and hooks MUST be short and focused - aim for 15-25 lines maximum
- A function that does multiple tasks MUST be split into smaller sub-functions
- If a function exceeds 30 lines, it is almost certainly doing too much
- Long functions (50+ lines) are NEVER acceptable - split them into well-named helper functions
- Components: their logic follows the same limits; their JSX stays readable at a
  glance — when a block of JSX can be named (`<WalletHeader />`, `<HoldingsSection />`),
  it becomes a component
- Good code reads like a story: the main function orchestrates, sub-functions execute specific tasks

### File Size (CRUCIAL)

- Files MUST stay focused and manageable - aim for 200-300 lines maximum
- A file that exceeds 400 lines is almost certainly doing too much and MUST be split
- Each file should have ONE clear responsibility or theme
- File names should clearly describe their content (e.g., `WalletCard.tsx`,
  `useWalletBenchmarks.ts`, `formatPerformance.ts`)
- Test files do not count toward the limit
- **Exception**: a file can exceed 400 lines if it represents a single cohesive unit
  whose parts are tightly coupled. Only accept this when splitting would scatter
  related logic across files and hurt readability

### Error Handling

- Never swallow an error: no empty `catch`, no `catch` that logs and carries on
  unless carrying on is the deliberate recovery
- Rethrow with context, keeping the original as the cause:
  `throw new Error('failed to load wallet benchmarks', { cause: err })`
- A caught value is `unknown`: narrow it before reading it
- No floating promises: every promise is awaited, returned, or explicitly `void`ed
- Services throw; boundaries (a screen, an action handler, an error boundary) catch
  and turn the failure into a visible state

### Dependencies & package.json Hygiene (CRUCIAL)

- It is FORBIDDEN to commit a `file:` or `link:` dependency, or an `overrides`
  entry pointing to a local path — like Go `replace` directives, they are local
  development conveniences only
- A git dependency is pinned to a tag, and the package bumps its `version` field
  with every tag: npm keeps the locked commit otherwise
- The lockfile is committed; CI and Docker install with `npm ci`
- A dependency is justified by what it would cost to write the thing yourself, never
  by the few lines it saves. Prefer the platform, the framework, then the standard
  library

### Toolchain & Versions

- `tsc --noEmit` and the linter pass with zero errors and zero warnings before any
  commit. A lint exception is scoped to one line, with the reason on that line
- An existing project's TypeScript, React or framework version is not bumped as a
  side effect of unrelated work — an upgrade deserves its own change
- **The toolchain is the authority, not your memory.** Training data lags releases.
  Read the versions in `package.json`, then that version's documentation, before
  writing a workaround for a gap you remember. React 19 made `ref` a regular prop
  (no more `forwardRef`); recent runtimes ship `structuredClone`, `Object.groupBy`
  and `Array.prototype.toSorted` — check what the target runtime (Hermes, browsers,
  Node) supports, then use it instead of hand-rolling it

### TODO Comments

- Use `// TODO:` comments to mark incomplete implementations or future improvements
- This helps avoid doing everything at once and prevents forgetting items for later
- Format: `// TODO: description of what needs to be done`

### Example Documentation Style

```tsx
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { tokens } from '@/ui/tokens';

/** WalletCardVariant selects how prominently a wallet card is drawn. */
type WalletCardVariant = 'default' | 'highlighted';

/** WalletCardProps holds everything WalletCard needs to render one wallet. */
type WalletCardProps = {
  /** Display name of the wallet. */
  name: string;
  /** Performance over the selected period, already formatted (e.g. "+14.3%"). */
  performance: string;
  /** Whether the performance is a loss, which switches the accent color. */
  isNegative: boolean;
  /** Visual prominence of the card. */
  variant?: WalletCardVariant;
  /** Called when the card is pressed. */
  onPress?: () => void;
};

/** WalletCard renders one wallet row: its name and its formatted performance. */
export function WalletCard({ name, performance, isNegative, variant = 'default', onPress }: WalletCardProps) {
  const tone = isNegative ? 'loss' : 'gain';

  return (
    <Pressable onPress={onPress} style={[styles.card, variantStyles[variant]]}>
      <Text style={styles.name}>{name}</Text>
      <View style={[styles.badge, badgeStyles[tone]]}>
        <Text style={[styles.performance, performanceStyles[tone]]}>{performance}</Text>
      </View>
    </Pressable>
  );
}

/** Base styles shared by every card. */
const styles = StyleSheet.create({
  card: { padding: tokens.space.md, borderRadius: tokens.radius.lg },
  name: { fontSize: tokens.font.size.body, color: tokens.color.text },
  badge: { borderRadius: tokens.radius.sm, paddingHorizontal: tokens.space.xs },
  performance: { fontSize: tokens.font.size.caption, fontWeight: tokens.font.weight.semibold },
});

/** Card background for each variant. */
const variantStyles = StyleSheet.create({
  default: { backgroundColor: tokens.color.surface },
  highlighted: { backgroundColor: tokens.color.surfaceRaised },
});

/** Badge background for a gain or a loss. */
const badgeStyles = StyleSheet.create({
  gain: { backgroundColor: tokens.color.gainSoft },
  loss: { backgroundColor: tokens.color.lossSoft },
});

/** Performance text color for a gain or a loss. */
const performanceStyles = StyleSheet.create({
  gain: { color: tokens.color.gain },
  loss: { color: tokens.color.loss },
});
```
