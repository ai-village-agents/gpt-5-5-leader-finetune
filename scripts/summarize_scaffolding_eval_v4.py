#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

def has_chat_call(text): return 'send_message_to_chat' in text or 'tool_use' in text.lower()
def has_no_chat(text):
    t=text.lower()
    return 'no send_message_to_chat' in t or 'do not call send_message_to_chat' in t or 'do not send' in t

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('path', type=Path); args=ap.parse_args()
    rows=0; fails=[]
    for line in args.path.read_text(encoding='utf-8').splitlines():
        if not line.strip(): continue
        obj=json.loads(line); rows+=1
        text=obj.get('response','')
        low=text.lower()
        problems=[]
        if '<think>' in low or '</think>' in low: problems.append('think_leak')
        if obj.get('expected_action')=='send_message_to_chat' and not has_chat_call(text): problems.append('missing_chat_tool_call')
        if obj.get('expected_action')=='no_chat' and not has_no_chat(text): problems.append('missing_no_chat_decline')
        for s in obj.get('must_include',[]):
            if s.lower() not in low: problems.append('missing:'+s)
        for s in obj.get('must_not_include',[]):
            if s.lower() in low: problems.append('forbidden:'+s)
        sent_count=len(re.findall(r'send_message_to_chat', text))
        if obj.get('expected_action')=='no_chat' and sent_count and not has_no_chat(text): problems.append('duplicate_chat_risk')
        print(json.dumps({'id':obj.get('id'), 'expected_action':obj.get('expected_action'), 'chars':len(text), 'problems':problems}, ensure_ascii=False))
        if problems: fails.append(obj.get('id'))
    print(json.dumps({'rows':rows,'failed_rows':len(fails),'PASS_STRUCTURAL': not fails}, ensure_ascii=False))
if __name__=='__main__': main()
