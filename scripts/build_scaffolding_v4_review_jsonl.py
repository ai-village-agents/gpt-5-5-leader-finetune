#!/usr/bin/env python3
"""Build a review JSONL from v4 scaffolding message-format rows.

This does not train. It concatenates known-good message-format rows into a
single auditable file for peer review and eventual SFT mixing.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("data/scaffolding_v4/scaffolding_v4_review.jsonl"))
    ap.add_argument("paths", nargs="+", type=Path, help="JSON files or directories containing *.json rows")
    args = ap.parse_args()
    files: list[Path] = []
    for p in args.paths:
        if p.is_dir():
            files.extend(sorted(p.glob("*.json")))
        else:
            files.append(p)
    rows = []
    for f in files:
        obj = load_json(f)
        obj.setdefault("_meta", {})["review_source_path"] = str(f)
        rows.append(obj)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows to {args.out}")
    # Reuse validator for final output.
    subprocess.run([sys.executable, "scripts/validate_scaffolding_messages_v4.py", str(args.out)], check=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
