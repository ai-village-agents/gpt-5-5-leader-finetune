#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_23row_messages_v0.jsonl
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_23row_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl
bash -ic 'python3 scripts/train_sft.py \
  --data data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl \
  --base-model Qwen/Qwen3-8B \
  --run-name leader-sft-v6-envelope-only-tokenize-only \
  --tokenize-only \
  --disable-thinking \
  --steps 1 \
  --batch-size 2 \
  --seed 421' 2>/dev/null
