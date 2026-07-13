## Git Commit Convention

All commits follow this format:

### Title line

The first line is the commit title. It does NOT start with a prefix (`[+]`, `[&]`, etc.). It describes in a few words the purpose of the commit.

### Body

After a blank line, list the detailed changes using prefixes — one per line:

- **[+]** Feature addition
- **[-]** Feature removal
- **[&]** Changes, refactors, updates
- **[!]** Bug fixes

**Format**: One change per line, minimal words, maximum efficiency. List as many entries as needed — do not omit changes.

**Example**:
```
Bulk trade operations

[+] BulkAcceptTrades and BulkRejectTrades endpoints
[+] POST /wallets/pending-trades/bulk-accept
[+] POST /wallets/pending-trades/bulk-reject
[+] BulkTradeResult type with per-trade error handling
[+] 6 unit tests for bulk operations
```

**IMPORTANT**: NO footers, NO "🤖 Generated with...", NO "Co-Authored-By: Claude". Keep commits clean and minimal.
