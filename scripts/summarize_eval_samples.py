#!/usr/bin/env python3
"""Summarize structural issues in held-out eval sample JSONL files.

This is not a substitute for manual rubric scoring, but it quickly flags common
leader-checkpoint failures: hidden-reasoning leakage, excessive length, empty
responses, missing action/fallback/validation cues, and stop_reason=length.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ACTION_RE = re.compile(r'\b(action|next|do|assign|draft|run|verify|check|test|commit|sample|score)\b', re.I)
FALLBACK_RE = re.compile(r'\b(fallback|if not|otherwise|if .* fails|else|revert|retry)\b', re.I)
VALIDATION_RE = re.compile(r'\b(validate|validation|verify|check|test|score|rubric|gate|evidence|criteria)\b', re.I)
DECISION_RE = re.compile(r'\b(decision|rule|criterion|criteria|threshold|gate|choose|decide)\b', re.I)


def sentence_count(text: str) -> int:
    stripped = re.sub(r'<think>.*?</think>', '', text, flags=re.I | re.S).strip()
    if not stripped:
        stripped = text.strip()
    parts = [p for p in re.split(r'(?<=[.!?])\s+', stripped) if p.strip()]
    return len(parts) if parts else (1 if stripped else 0)


def has_length_stop(row: dict) -> bool:
    raw = row.get('raw_response') or row.get('raw') or ''
    return 'stop_reason=\'length\'' in raw or 'stop_reason="length"' in raw or "STOP_REASON_LENGTH" in raw


def summarize(path: Path) -> tuple[int, int]:
    rows = 0
    failures = 0
    for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            continue
        rows += 1
        row = json.loads(line)
        text = str(row.get('response', ''))
        metrics = {
            'chars': len(text),
            'sentences': sentence_count(text),
            'empty': not text.strip(),
            'think_leak': '<think>' in text.lower() or '</think>' in text.lower(),
            'too_long_chars': len(text) > 600,
            'too_many_sentences': sentence_count(text) > 4,
            'length_stop': has_length_stop(row),
            'has_action_cue': bool(ACTION_RE.search(text)),
            'has_fallback_cue': bool(FALLBACK_RE.search(text)),
            'has_validation_cue': bool(VALIDATION_RE.search(text)),
            'has_decision_cue': bool(DECISION_RE.search(text)),
        }
        hard_flags = [k for k in ('empty','think_leak','too_long_chars','too_many_sentences','length_stop') if metrics[k]]
        soft_missing = [k for k in ('has_action_cue','has_fallback_cue','has_validation_cue','has_decision_cue') if not metrics[k]]
        status = 'PASS-CANDIDATE' if not hard_flags and not soft_missing else 'REVIEW'
        if status != 'PASS-CANDIDATE':
            failures += 1
        print(json.dumps({
            'file': str(path),
            'line': i,
            'scenario_id': row.get('scenario_id'),
            'status': status,
            'hard_flags': hard_flags,
            'soft_missing': soft_missing,
            'metrics': metrics,
        }, ensure_ascii=False))
    if rows == 0:
        raise SystemExit(f'FAIL: {path}: no rows')
    print(f'SUMMARY {path}: rows={rows} review={failures} pass_candidate={rows-failures}')
    return rows, failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='+')
    args = ap.parse_args()
    total_rows = total_failures = 0
    for name in args.paths:
        rows, failures = summarize(Path(name))
        total_rows += rows
        total_failures += failures
    return 0 if total_failures == 0 else 1

if __name__ == '__main__':
    raise SystemExit(main())
