#!/usr/bin/env python3
"""Print one-at-a-time live shakedown prompts from eval/scenarios_v0.jsonl."""
import argparse, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--scenarios', default='eval/scenarios_v0.jsonl')
parser.add_argument('--id', help='Only print one scenario id')
parser.add_argument('--max-sentences', type=int, default=4)
args = parser.parse_args()

rows=[]
for line in Path(args.scenarios).read_text().splitlines():
    line=line.strip()
    if not line:
        continue
    row=json.loads(line)
    if args.id and row['id'] != args.id:
        continue
    rows.append(row)

if args.id and not rows:
    raise SystemExit(f'No scenario with id {args.id!r}')

for row in rows:
    print(f"## {row['id']} ({row.get('category','')})")
    print(f"[Temporary] Fine-tuned Leader: live shakedown scenario {row['id']}. Please answer as #best leader in {args.max_sentences} sentences max. Scenario: {row['prompt']}")
    print()
