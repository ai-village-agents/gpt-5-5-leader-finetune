#!/usr/bin/env python3
"""Validate project JSONL files for basic shape."""
from __future__ import annotations
import json, sys
from pathlib import Path

def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)

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
        if path.name.startswith('sft_schema'):
            if 'messages' not in obj or len(obj['messages']) != 3:
                fail(f"{path}:{i}: expected 3-message schema example")
    print(f"OK {path}: {rows} rows")

for arg in sys.argv[1:] or ['eval/scenarios_v0.jsonl','data/sft_schema_v0.jsonl']:
    validate(Path(arg))
