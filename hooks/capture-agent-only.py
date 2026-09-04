#!/usr/bin/env python3
"""PreToolUse hook: the capture browser is driven by the `capture` agent, never
by the main thread.

Inert unless the session was started with CLAUDE_CAPTURE_AGENT_ONLY=1 (the
`glm` lab runner sets it). Inside a subagent the call is allowed — its input
carries `agent_id`. On the main thread, any `mcp__capture__*` tool is refused
(exit 2) with the instruction to dispatch the `capture` agent with a tour.

Why a hook and not `--disallowedTools mcp__capture`: measured on 4 September
2026, the flag strips the tools from subagents as well, and the `capture`
agent then has nothing to drive with. A hook sees who is calling.
"""
import json
import os
import sys

if os.environ.get("CLAUDE_CAPTURE_AGENT_ONLY") != "1":
    sys.exit(0)

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if data.get("agent_id"):
    sys.exit(0)

tool = data.get("tool_name") or ""
if not tool.startswith("mcp__capture__"):
    sys.exit(0)

sys.stderr.write(
    "Refused: the capture browser is the `capture` agent's, not this thread's. "
    "Dispatch it (Agent tool, subagent_type \"capture\") with a tour — network, "
    "start URL, actions in order, the calls to look at, logged in or not — and "
    "read the archive it names with lab/tools/capture.py.\n"
)
sys.exit(2)
