#!/usr/bin/env python3
"""Build a candidate v4 SFT dataset by mixing v3-style rows with scaffolding rows.

This script is deliberately conservative: it validates all rows have three chat
messages and writes a reviewable JSONL with source tags. It does not launch
Tinker training.
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROLES = ["system", "user", "assistant"]


def sanitize_assistant_text(text: str) -> str:
    """Avoid placing literal think tags in assistant targets, even as examples."""
    return text.replace("<think>", "the visible think tag").replace("</think>", "the visible closing think tag")


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                yield line_no, json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{line_no}: invalid JSON: {e}")


def validate_messages(obj: dict, path: Path, line_no: int) -> None:
    msgs = obj.get("messages")
    if not isinstance(msgs, list) or len(msgs) != 3:
        raise SystemExit(f"{path}:{line_no}: expected messages list of length 3")
    roles = [m.get("role") for m in msgs if isinstance(m, dict)]
    if roles != ROLES:
        raise SystemExit(f"{path}:{line_no}: expected roles {ROLES}, got {roles}")
    for i, m in enumerate(msgs):
        if not isinstance(m.get("content"), str) or not m["content"].strip():
            raise SystemExit(f"{path}:{line_no}: empty content in message {i}")
    # Literal think tags are sanitized during normalization before final validation.


def normalize(row: dict, source_family: str, path: Path, line_no: int) -> dict:
    validate_messages(row, path, line_no)
    tags = list(row.get("tags", [])) if isinstance(row.get("tags"), list) else []
    if source_family not in tags:
        tags.append(source_family)
    return {
        "messages": [
            row["messages"][0],
            row["messages"][1],
            {**row["messages"][2], "content": sanitize_assistant_text(row["messages"][2]["content"])},
        ],
        "source": row.get("source") or row.get("_meta", {}).get("captured_by") or source_family,
        "split": row.get("split", "train"),
        "tags": tags,
        "component_file": row.get("component_file") or row.get("_meta", {}).get("review_source_path") or str(path),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, default=Path("data/heldin_sft_v1.jsonl"))
    ap.add_argument("--scaffolding", type=Path, default=Path("data/scaffolding_v4/scaffolding_v4_review.jsonl"))
    ap.add_argument("--out", type=Path, default=Path("data/heldin_sft_v4_candidate.jsonl"))
    args = ap.parse_args()
    rows = []
    counts = {"base": 0, "scaffolding_v4": 0}
    for line_no, row in read_jsonl(args.base):
        rows.append(normalize(row, "base_leader_sft", args.base, line_no))
        counts["base"] += 1
    for line_no, row in read_jsonl(args.scaffolding):
        rows.append(normalize(row, "scaffolding_v4", args.scaffolding, line_no))
        counts["scaffolding_v4"] += 1
    ids = set()
    # Dedupe exact message triples while preserving order.
    deduped = []
    for row in rows:
        key = json.dumps(row["messages"], sort_keys=True, ensure_ascii=False)
        if key not in ids:
            ids.add(key)
            if "<think>" in row["messages"][-1]["content"].lower() or "</think>" in row["messages"][-1]["content"].lower():
                raise SystemExit("sanitization failed: assistant target still contains think tag")
            deduped.append(row)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for row in deduped:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"base_rows={counts['base']}")
    print(f"scaffolding_rows={counts['scaffolding_v4']}")
    print(f"output_rows={len(deduped)}")
    print(f"out={args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
