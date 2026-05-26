#!/usr/bin/env python3
"""Import peer-mined leader SFT data into GPT-5.5's local held-in schema.

Inputs are public GitHub artifacts from #best peers:
- Kimi K2.6 HF chat JSONL
- Claude Opus 4.7 mined Markdown with SITUATION/QUOTE pairs

Outputs are normalized local held-in JSONL component files with split/tags/id so
scripts/validate_jsonl.py can gate them before training.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.request import urlopen

KIMI_URL = 'https://raw.githubusercontent.com/ai-village-agents/k2-6-memory/main/finetune/data/mined_kimi_v0.jsonl'
CLAUDE_URL = 'https://raw.githubusercontent.com/ai-village-agents/claude-opus-4-7-memory/main/finetune/mined_leader_messages_d405_409.md'
LOCAL_SYSTEM_PROMPT = 'You are the #best leader for AI Village. Coordinate agents under uncertainty, validate before irreversible action, preserve peer agency, and keep responses concise and operational.'


def fetch_text(url: str) -> str:
    with urlopen(url, timeout=30) as response:
        return response.read().decode('utf-8')


def normalize_row(row: dict, *, row_id: str, source_prefix: str, tags: list[str], normalize_system: bool) -> dict:
    messages = row.get('messages')
    if not isinstance(messages, list) or len(messages) != 3:
        raise ValueError(f'{row_id}: expected 3 messages')
    normalized_messages = []
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict) or msg.get('role') not in ('system', 'user', 'assistant'):
            raise ValueError(f'{row_id}: malformed message {i+1}')
        content = msg.get('content')
        if not isinstance(content, str) or not content.strip():
            raise ValueError(f'{row_id}: empty message {i+1}')
        normalized_messages.append({'role': msg['role'], 'content': content.strip()})
    if [m['role'] for m in normalized_messages] != ['system', 'user', 'assistant']:
        raise ValueError(f'{row_id}: expected system/user/assistant roles')
    if normalize_system:
        normalized_messages[0]['content'] = LOCAL_SYSTEM_PROMPT
    source = row.get('source') or source_prefix
    return {
        'id': row_id,
        'messages': normalized_messages,
        'source': f'{source_prefix}: {source}',
        'split': 'train',
        'tags': tags,
    }


def import_kimi(text: str, *, normalize_system: bool) -> list[dict]:
    rows = []
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        rows.append(normalize_row(
            row,
            row_id=f'peer-kimi-d405-409-{i:02d}',
            source_prefix='peer-kimi-mined-d405-409',
            tags=['peer-mined', 'coordination', 'validation', 'decision-rule'],
            normalize_system=normalize_system,
        ))
    return rows


def import_claude(text: str, *, normalize_system: bool) -> list[dict]:
    rows = []
    current_title = None
    situation = None
    quote = None
    for raw in text.splitlines() + ['## END']:
        line = raw.strip()
        if line.startswith('## '):
            if situation and quote:
                idx = len(rows) + 1
                rows.append(normalize_row(
                    {
                        'messages': [
                            {'role': 'system', 'content': LOCAL_SYSTEM_PROMPT},
                            {'role': 'user', 'content': situation},
                            {'role': 'assistant', 'content': quote},
                        ],
                        'source': current_title or f'Claude mined row {idx}',
                    },
                    row_id=f'peer-claude-d405-409-{idx:02d}',
                    source_prefix='peer-claude-mined-d405-409',
                    tags=['peer-mined', 'coordination', 'validation', 'decision-rule'],
                    normalize_system=normalize_system,
                ))
            current_title = re.sub(r'^##\s*', '', line).strip()
            situation = None
            quote = None
            continue
        if line.startswith('- SITUATION:'):
            situation = line.split(':', 1)[1].strip()
        elif line.startswith('- QUOTE:'):
            quote = line.split(':', 1)[1].strip()
            if len(quote) >= 2 and quote[0] == quote[-1] == '"':
                quote = quote[1:-1]
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--kimi-url', default=KIMI_URL)
    ap.add_argument('--claude-url', default=CLAUDE_URL)
    ap.add_argument('--kimi-out', default='data/heldin_sft_peer_kimi_v0.jsonl')
    ap.add_argument('--claude-out', default='data/heldin_sft_peer_claude_v0.jsonl')
    ap.add_argument('--preserve-peer-system', action='store_true', help='keep peer system prompts instead of normalizing to local system prompt')
    args = ap.parse_args()

    normalize_system = not args.preserve_peer_system
    kimi_rows = import_kimi(fetch_text(args.kimi_url), normalize_system=normalize_system)
    claude_rows = import_claude(fetch_text(args.claude_url), normalize_system=normalize_system)
    if not kimi_rows:
        raise SystemExit('no Kimi rows imported')
    if not claude_rows:
        raise SystemExit('no Claude rows imported')
    write_jsonl(Path(args.kimi_out), kimi_rows)
    write_jsonl(Path(args.claude_out), claude_rows)
    print(f'wrote {args.kimi_out}: {len(kimi_rows)} rows')
    print(f'wrote {args.claude_out}: {len(claude_rows)} rows')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
