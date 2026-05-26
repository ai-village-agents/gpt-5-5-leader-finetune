#!/usr/bin/env python3
"""Validate normalized v4 scaffolding JSONL rows."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REQUIRED_TOP = [
    "id", "source_agent", "day", "room", "turn_type", "system_prompt_excerpt",
    "developer_tool_contract_excerpt", "events_log_since_last_turn", "environment_state",
    "assistant_action", "target_behavior_notes", "anti_behavior_notes",
]
VALID_TURN_TYPES = {
    "positive_chat_tool_call", "negative_no_chat", "negative_wrong_frame",
    "positive_repo_work_then_chat", "positive_no_chat_repo_work",
}
VALID_ACTION_KINDS = {"tool_call", "no_chat", "repo_work"}


def fail(path: Path, line_no: int, msg: str) -> None:
    raise SystemExit(f"{path}:{line_no}: {msg}")


def validate_row(row: dict, path: Path, line_no: int) -> None:
    for key in REQUIRED_TOP:
        if key not in row:
            fail(path, line_no, f"missing required key {key!r}")
    if row["turn_type"] not in VALID_TURN_TYPES:
        fail(path, line_no, f"invalid turn_type {row['turn_type']!r}")
    if not isinstance(row["events_log_since_last_turn"], list) or not row["events_log_since_last_turn"]:
        fail(path, line_no, "events_log_since_last_turn must be a non-empty list")
    for i, event in enumerate(row["events_log_since_last_turn"]):
        if not isinstance(event, dict):
            fail(path, line_no, f"event {i} is not an object")
        for key in ("actionType", "agentName", "createdAt"):
            if key not in event:
                fail(path, line_no, f"event {i} missing {key!r}")
    action = row["assistant_action"]
    if not isinstance(action, dict):
        fail(path, line_no, "assistant_action must be an object")
    if action.get("kind") not in VALID_ACTION_KINDS:
        fail(path, line_no, f"invalid assistant_action.kind {action.get('kind')!r}")
    if action.get("kind") == "tool_call":
        if action.get("tool_name") != "send_message_to_chat":
            fail(path, line_no, "tool_call rows must use send_message_to_chat for v4 chat examples")
        msg = action.get("arguments", {}).get("message")
        if not isinstance(msg, str) or not msg.strip():
            fail(path, line_no, "send_message_to_chat action requires non-empty arguments.message")
    joined = json.dumps(row, ensure_ascii=False).lower()
    if "<think>" in joined or "</think>" in joined:
        # Allowed only in anti-behavior or failure-description context, not target action text.
        msg = action.get("arguments", {}).get("message", "").lower()
        if "<think>" in msg or "</think>" in msg:
            fail(path, line_no, "target chat message must not contain think tags")
    for key in ("target_behavior_notes", "anti_behavior_notes"):
        if not isinstance(row[key], list) or not all(isinstance(x, str) and x.strip() for x in row[key]):
            fail(path, line_no, f"{key} must be a non-empty list of strings")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args()
    rows = 0
    for path in args.paths:
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    fail(path, line_no, f"invalid JSON: {e}")
                validate_row(row, path, line_no)
                rows += 1
    print(f"validated scaffolding v4 rows: {rows}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
