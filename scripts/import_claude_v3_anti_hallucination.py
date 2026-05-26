#!/usr/bin/env python3
"""Import Claude Opus 4.7 v3 anti-hallucination rows into local held-in schema."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from urllib.request import urlopen

URL = 'https://raw.githubusercontent.com/ai-village-agents/claude-opus-4-7-memory/main/finetune/data/seed_v3.jsonl'
LOCAL_SYSTEM_PROMPT = (
    'You are the #best leader for AI Village. Coordinate agents under uncertainty, '
    'validate before irreversible action, preserve peer agency, make reversible decisions, '
    'and keep responses concise, calm, evidence-seeking, and operational. '
    'Do not reveal hidden chain-of-thought or emit <think> tags; provide only the final operational answer.'
)

def fetch_text(url: str) -> str:
    with urlopen(url, timeout=30) as response:
        return response.read().decode('utf-8')

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--url', default=URL)
    ap.add_argument('--out', default='data/heldin_sft_peer_claude_v3_anti_hallucination.jsonl')
    args=ap.parse_args()
    rows=[]
    for i,line in enumerate(fetch_text(args.url).splitlines(),1):
        if not line.strip():
            continue
        obj=json.loads(line)
        if obj.get('source') != 'anti_hallucination_v3':
            continue
        msgs=obj.get('messages')
        if not isinstance(msgs, list) or [m.get('role') for m in msgs] != ['system','user','assistant']:
            raise ValueError(f'bad messages on source row {i}')
        normalized=[dict(m) for m in msgs]
        normalized[0]['content']=LOCAL_SYSTEM_PROMPT
        rows.append({
            'id': f'peer-claude-v3-anti-hallucination-{len(rows)+1:02d}',
            'messages': normalized,
            'source': 'peer-claude-v3: anti_hallucination_v3',
            'split': 'train',
            'tags': ['peer-mined','anti-hallucination','grounding','validation','decision-rule'],
        })
    if not rows:
        raise SystemExit('no anti_hallucination_v3 rows found')
    out=Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':'))+'\n')
    print(f'wrote {out}: {len(rows)} rows')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
