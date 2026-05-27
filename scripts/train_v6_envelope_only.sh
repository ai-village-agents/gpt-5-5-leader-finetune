#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TINKER_API_KEY:?TINKER_API_KEY must be set; run through bash -ic if needed}"
python3 scripts/train_sft.py \
  --data data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl \
  --base-model Qwen/Qwen3-8B \
  --rank 32 \
  --steps 80 \
  --learning-rate 5e-5 \
  --batch-size 4 \
  --seed 421 \
  --run-name leader-sft-v6-envelope-only \
  --disable-thinking \
  --no-dry-run
