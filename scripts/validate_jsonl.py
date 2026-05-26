#!/usr/bin/env python3
"""Validate project JSONL files for basic shape."""
from __future__ import annotations
import json, sys
from pathlib import Path

def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

def validate_messages(path: Path, i: int, obj: dict, *, schema_example: bool=False) -> None:
    msgs=obj.get('messages')
    if not isinstance(msgs, list) or len(msgs) != 3:
        fail(f"{path}:{i}: expected exactly 3 messages")
    roles=[m.get('role') for m in msgs if isinstance(m, dict)]
    if roles != ['system','user','assistant']:
        fail(f"{path}:{i}: expected system/user/assistant roles, got {roles!r}")
    for j,m in enumerate(msgs,1):
        if not isinstance(m.get('content'), str) or not m['content'].strip():
            fail(f"{path}:{i}: message {j} content must be non-empty string")
    if not schema_example:
        if obj.get('split') not in ('train','heldout'):
            fail(f"{path}:{i}: split must be train or heldout")
        if not isinstance(obj.get('source'), str) or not obj['source'].strip():
            fail(f"{path}:{i}: source must be non-empty string")
        if not isinstance(obj.get('tags'), list) or not all(isinstance(t, str) and t for t in obj['tags']):
            fail(f"{path}:{i}: tags must be non-empty list of strings")

def validate(path: Path):
    rows=0
    for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():
            continue
        rows += 1
        try:
            obj=json.loads(line)
        except Exception as e:
            fail(f"{path}:{i}: invalid JSON: {e}")
        if path.name.startswith('scenarios'):
            for key in ['id','category','prompt','target_traits']:
                if key not in obj:
                    fail(f"{path}:{i}: missing {key}")
            if not isinstance(obj['target_traits'], list) or not obj['target_traits']:
                fail(f"{path}:{i}: target_traits must be non-empty list")
        elif path.name.startswith('sft_schema'):
            validate_messages(path, i, obj, schema_example=True)
        elif path.name.startswith('heldin_sft'):
            validate_messages(path, i, obj, schema_example=False)
        elif path.name.startswith('manual_score_template'):
            if not isinstance(obj.get('scenario_id'), str) or not obj['scenario_id']:
                fail(f"{path}:{i}: missing scenario_id")
            scores=obj.get('scores')
            if not isinstance(scores, dict) or not scores:
                fail(f"{path}:{i}: missing scores object")
    if rows == 0:
        fail(f"{path}: no rows")
    print(f"OK {path}: {rows} rows")

def default_paths() -> list[str]:
    paths=['eval/scenarios_v0.jsonl','data/sft_schema_v0.jsonl','eval/manual_score_template.jsonl']
    paths += sorted(str(p) for p in Path('data').glob('heldin_sft*.jsonl'))
    return paths

for arg in sys.argv[1:] or default_paths():
    validate(Path(arg))
