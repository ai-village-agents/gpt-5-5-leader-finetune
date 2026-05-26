#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
VALID_ACTIONS={"send_message_to_chat","no_chat","repo_work"}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('path', type=Path); args=ap.parse_args()
    rows=0
    for i,line in enumerate(args.path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        obj=json.loads(line); rows+=1
        for k in ['id','expected_action','must_include','must_not_include','prompt','scoring_notes']:
            if k not in obj: raise SystemExit(f'{args.path}:{i}: missing {k}')
        if obj['expected_action'] not in VALID_ACTIONS: raise SystemExit(f'{args.path}:{i}: bad expected_action')
        msgs=obj['prompt'].get('messages')
        if not isinstance(msgs,list) or [m.get('role') for m in msgs] != ['system','user']:
            raise SystemExit(f'{args.path}:{i}: prompt.messages must be system,user')
        if 'Here is what has happened' not in msgs[1].get('content',''):
            raise SystemExit(f'{args.path}:{i}: user prompt should preserve event-log phrasing')
        if not isinstance(obj['must_include'],list) or not isinstance(obj['must_not_include'],list):
            raise SystemExit(f'{args.path}:{i}: include/exclude must be lists')
    print(f'validated scaffolding eval rows: {rows}')
if __name__=='__main__': main()
