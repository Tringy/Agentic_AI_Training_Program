#!/usr/bin/env python3
"""
PreToolUse hook — ask for confirmation before destructive terminal commands.
Reads tool invocation JSON from stdin, outputs a permissionDecision if needed.
"""
import json
import sys

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
tool_input = data.get("tool_input", {})

DESTRUCTIVE_PATTERNS = [
    "fly deploy",
    "fly destroy",
    "fly apps destroy",
    "rm -rf",
    "git push --force",
    "git push -f",
    "git reset --hard",
    "DROP TABLE",
]

if tool in ("run_in_terminal", "bash", "execute_command"):
    command = tool_input.get("command", "") or tool_input.get("cmd", "")
    for pattern in DESTRUCTIVE_PATTERNS:
        if pattern.lower() in command.lower():
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": (f"Destructive command detected ('{pattern}') — confirm before proceeding"),
                }
            }
            print(json.dumps(output))
            sys.exit(0)

sys.exit(0)
