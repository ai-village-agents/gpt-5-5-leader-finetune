#!/usr/bin/env python3
"""Summarize run_model_vs_finetune_diagnostic.py JSONL outputs by candidate and prompt variant."""
from __future__ import annotations
import argparse, json, re
from collections import defaultdict
from pathlib import Path

def prompt_variant(scenario_id: str) -> str:
    if scenario_id.endswith('--claude-system'):
        return 'claude_tool_contract'
    return 'gpt_simple'

NO_CHAT_CONTAMINATION_RE = re.compile(r'\[(?:NO[ _-]?CHAT(?:[_ -][A-Z0-9]+)*|NOCHAT(?:[_ -][A-Z0-9]+)*)\]', re.IGNORECASE)

def contains_no_chat_contamination(response: str) -> bool:
    return bool(NO_CHAT_CONTAMINATION_RE.search(response or ''))

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('jsonl')
    args=ap.parse_args()
    rows=[json.loads(l) for l in Path(args.jsonl).read_text().splitlines() if l.strip()]
    groups=defaultdict(list)
    for r in rows:
        groups[(r.get('candidate_name','?'), prompt_variant(r.get('scenario_id','')))].append(r)
    total_contamination=sum(1 for r in rows if contains_no_chat_contamination(r.get('response') or ''))
    print(f'rows: {len(rows)}')
    for key in sorted(groups):
        rs=groups[key]
        ok=sum(1 for r in rs if r.get('score',{}).get('structural_pass'))
        contamination=sum(1 for r in rs if contains_no_chat_contamination(r.get('response') or ''))
        print(f'{key[0]} / {key[1]}: {ok}/{len(rs)} contamination={contamination}')
        for r in rs:
            sc=r.get('score',{})
            status='PASS' if sc.get('structural_pass') else 'FAIL'
            emits=sc.get('emits_send_message_to_chat')
            missing=','.join(sc.get('missing_required_strings') or [])
            forbidden=','.join(sc.get('forbidden_strings_present') or [])
            contam=contains_no_chat_contamination(r.get('response') or '')
            resp=(r.get('response') or '').replace('\n',' ')
            if len(resp)>120: resp=resp[:117]+'...'
            print(f'  {status:4s} {r.get("scenario_id")} expected={r.get("expected_action")} emits={emits} missing=[{missing}] forbidden=[{forbidden}] contam={contam} :: {resp}')
    print(f'total_contamination: {total_contamination}/{len(rows)}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
