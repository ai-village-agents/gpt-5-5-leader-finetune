#!/usr/bin/env python3
"""Validate v4 scaffolding rows in chat-format JSON/JSONL.

Accepts Claude-style one-row JSON files or JSONL files whose rows contain a
`messages` list. This is intentionally lightweight: it validates shape and key
anti-failure properties before concatenation/training review.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROLE_SEQ = ["system", "user", "assistant"]


def iter_rows(path: Path):
    if path.suffix == ".jsonl":
        with path.open(encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if line.strip():
                    yield line_no, json.loads(line)
    else:
        yield 1, json.loads(path.read_text(encoding="utf-8"))


def fail(path: Path, line_no: int, msg: str) -> None:
    raise SystemExit(f"{path}:{line_no}: {msg}")


def validate(row: dict, path: Path, line_no: int) -> None:
    messages = row.get("messages")
    if not isinstance(messages, list) or len(messages) != 3:
        fail(path, line_no, "messages must be a three-item list")
    roles = [m.get("role") for m in messages if isinstance(m, dict)]
    if roles != ROLE_SEQ:
        fail(path, line_no, f"roles must be {ROLE_SEQ}, got {roles}")
    for i, msg in enumerate(messages):
        if not isinstance(msg.get("content"), str) or not msg["content"].strip():
            fail(path, line_no, f"message {i} has empty content")
    system, user, assistant = [m["content"] for m in messages]
    if "[Temporary] Fine-tuned Leader" not in system:
        fail(path, line_no, "system content should adapt identity to [Temporary] Fine-tuned Leader")
    if "Here is what has happened since you started your session" not in user:
        fail(path, line_no, "user content should preserve scaffolding event-log phrase")
    assistant_lower = assistant.lower()
    if "<think>" in assistant_lower or "</think>" in assistant_lower:
        fail(path, line_no, "assistant content must not contain think tags")
    has_tool = "send_message_to_chat" in assistant
    says_no_chat = "no send_message_to_chat" in assistant_lower or "do not call send_message_to_chat" in assistant_lower
    if not (has_tool or says_no_chat):
        fail(path, line_no, "assistant should either use or explicitly decline send_message_to_chat")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    args = ap.parse_args()
    rows = 0
    for path in args.paths:
        for line_no, row in iter_rows(path):
            validate(row, path, line_no)
            rows += 1
    print(f"validated v4 message-format rows: {rows}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
