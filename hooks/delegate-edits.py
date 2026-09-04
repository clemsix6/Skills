#!/usr/bin/env python3
"""PreToolUse hook: in a two-tier session, the main thread does not write code.

Inert unless the session was started with CLAUDE_DELEGATE_EDITS=1 (the `glm`
alias sets it; `cc` never does). Inside a subagent the call is allowed. On the
main thread, an Edit/Write/MultiEdit/NotebookEdit on anything but prose is
refused (exit 2) with the instruction to dispatch the `implement` agent — the
same rule glm-delegation.md states.

Prose is free: Markdown and text files, anything under a docs/ directory, and
the scratch locations a thread writes its briefs and reports to.
"""
import json
import os
import sys

if os.environ.get("CLAUDE_DELEGATE_EDITS") != "1":
    sys.exit(0)

data = json.load(sys.stdin)
if data.get("agent_id"):
    sys.exit(0)

tool_input = data.get("tool_input") or {}
path = os.path.abspath(tool_input.get("file_path") or tool_input.get("notebook_path") or "")
home = os.path.expanduser("~")
prose_suffixes = (".md", ".markdown", ".txt", ".rst")
free_prefixes = ("/tmp/", "/private/tmp/",
                 os.path.join(home, "missions") + "/",
                 os.path.join(home, ".claude") + "/",
                 os.path.join(home, ".hermes") + "/")
if path.endswith(prose_suffixes) or path.startswith(free_prefixes) or "/docs/" in path:
    sys.exit(0)

shown = os.path.relpath(path, data.get("cwd") or os.getcwd())
sys.stderr.write(
    f"Refused: this thread reads, decides and reviews; it does not write code ({shown}). "
    "Dispatch the `implement` subagent (Agent tool, subagent_type \"implement\") with the exact "
    "change, the files and the verification commands, then review what it returns. "
    "Prose (.md, .txt, docs/) stays yours.\n")
sys.exit(2)
