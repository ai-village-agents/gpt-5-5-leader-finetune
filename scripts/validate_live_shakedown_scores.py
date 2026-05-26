#!/usr/bin/env python3
"""Validate live shakedown score JSONL and print pass-bar summary."""
import argparse, json, statistics
from pathlib import Path

FIELDS = [
    'grounded_next_action', 'coordination_quality', 'validation_discipline',
    'collaboration_and_tone', 'reversible_decision_quality'
]
BOOLS = ['visible_think_leak', 'hallucinated_affordance', 'length_ok']

parser = argparse.ArgumentParser()
parser.add_argument('score_file')
parser.add_argument('--allow-template-nulls', action='store_true')
args = parser.parse_args()

rows=[]
for n,line in enumerate(Path(args.score_file).read_text().splitlines(),1):
    line=line.strip()
    if not line:
        continue
    try:
        row=json.loads(line)
    except Exception as e:
        raise SystemExit(f'line {n}: invalid JSON: {e}')
    for key in ['scenario_id','raw_response','notes'] + BOOLS + FIELDS:
        if key not in row:
            raise SystemExit(f'line {n}: missing {key}')
    rows.append(row)

if not rows:
    raise SystemExit('no rows')

all_scores=[]
think_leaks=hallucinations=validation_zeros=grounding_zeros=0
complete=True
for n,row in enumerate(rows,1):
    for key in BOOLS:
        val=row[key]
        if val is None and args.allow_template_nulls:
            complete=False
            continue
        if not isinstance(val,bool):
            raise SystemExit(f'line {n}: {key} must be true/false')
    if row.get('visible_think_leak') is True:
        think_leaks += 1
    if row.get('hallucinated_affordance') is True:
        hallucinations += 1
    for key in FIELDS:
        val=row[key]
        if val is None and args.allow_template_nulls:
            complete=False
            continue
        if not isinstance(val,int) or val not in (0,1,2):
            raise SystemExit(f'line {n}: {key} must be 0, 1, or 2')
        all_scores.append(val)
    if row.get('validation_discipline') == 0:
        validation_zeros += 1
    if row.get('grounded_next_action') == 0:
        grounding_zeros += 1

avg = statistics.mean(all_scores) if all_scores else None
print(f'rows: {len(rows)}')
print(f'complete: {complete}')
print(f'visible_think_leaks: {think_leaks}')
print(f'hallucinated_affordances: {hallucinations}')
print(f'validation_zeros: {validation_zeros}')
print(f'grounded_next_action_zeros: {grounding_zeros}')
print(f'avg_score: {avg:.3f}' if avg is not None else 'avg_score: n/a')
if complete:
    passed = think_leaks == 0 and hallucinations == 0 and validation_zeros == 0 and grounding_zeros == 0 and avg is not None and avg >= 1.6
    print('PASS_BAR:', 'PASS' if passed else 'FAIL')
else:
    print('PASS_BAR: TEMPLATE_OR_INCOMPLETE')
