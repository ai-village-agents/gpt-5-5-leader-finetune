#!/usr/bin/env python3
"""Build combined held-in SFT datasets from validated component JSONL files."""
from __future__ import annotations
import argparse, json
from pathlib import Path

DEFAULT_INPUTS = [
    'data/heldin_sft_seed_v0.jsonl',
    'data/heldin_sft_day405_409_v0.jsonl',
    'data/heldin_sft_peer_kimi_v0.jsonl',
    'data/heldin_sft_peer_claude_v0.jsonl',
]


def load(path: Path) -> list[dict]:
    rows=[]
    for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():
            continue
        obj=json.loads(line)
        obj.setdefault('component_file', str(path))
        rows.append(obj)
    if not rows:
        raise ValueError(f'{path}: no rows')
    return rows


def row_key(row: dict) -> str:
    if row.get('id'):
        return f"id:{row['id']}"
    msgs=row.get('messages') or []
    assistant=(msgs[-1].get('content','') if msgs else '')
    user=(msgs[-2].get('content','') if len(msgs) >= 2 else '')
    return f"content:{user[:120]}::{assistant[:120]}"


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--inputs', nargs='*', default=DEFAULT_INPUTS)
    ap.add_argument('--output', default='data/heldin_sft_v1.jsonl')
    args=ap.parse_args()
    seen=set()
    combined=[]
    for name in args.inputs:
        for row in load(Path(name)):
            key=row_key(row)
            if key in seen:
                print(f'skip duplicate {key}')
                continue
            seen.add(key)
            combined.append(row)
    out=Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        for row in combined:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'wrote {out}: {len(combined)} rows from {len(args.inputs)} component files')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
