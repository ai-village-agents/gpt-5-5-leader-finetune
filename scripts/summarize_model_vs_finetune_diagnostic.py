#!/usr/bin/env python3
"""Summarize run_model_vs_finetune_diagnostic.py JSONL outputs by candidate and prompt variant."""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path

def prompt_variant(scenario_id: str) -> str:
    if scenario_id.endswith('--claude-system'):
        return 'claude_tool_contract'
    return 'gpt_simple'

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('jsonl')
    args=ap.parse_args()
    rows=[json.loads(l) for l in Path(args.jsonl).read_text().splitlines() if l.strip()]
    groups=defaultdict(list)
    for r in rows:
        groups[(r.get('candidate_name','?'), prompt_variant(r.get('scenario_id','')))].append(r)
    print(f'rows: {len(rows)}')
    for key in sorted(groups):
        rs=groups[key]
        ok=sum(1 for r in rs if r.get('score',{}).get('structural_pass'))
        print(f'{key[0]} / {key[1]}: {ok}/{len(rs)}')
        for r in rs:
            sc=r.get('score',{})
            status='PASS' if sc.get('structural_pass') else 'FAIL'
            emits=sc.get('emits_send_message_to_chat')
            missing=','.join(sc.get('missing_required_strings') or [])
            forbidden=','.join(sc.get('forbidden_strings_present') or [])
            resp=(r.get('response') or '').replace('\n',' ')
            if len(resp)>120: resp=resp[:117]+'...'
            print(f'  {status:4s} {r.get("scenario_id")} expected={r.get("expected_action")} emits={emits} missing=[{missing}] forbidden=[{forbidden}] :: {resp}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
