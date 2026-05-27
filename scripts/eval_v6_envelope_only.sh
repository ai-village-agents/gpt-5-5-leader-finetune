#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "usage: $0 tinker://.../sampler_weights/leader-sft-v6-envelope-only" >&2
  exit 2
fi
uri="$1"
cd "$(dirname "$0")/.."
python3 scripts/run_model_vs_finetune_diagnostic.py \
  --candidate "v6=${uri}" \
  --candidate qwen3_8b=Qwen/Qwen3-8B \
  --candidate leader_sft_v4=tinker://bde4da6e-eacc-5a2e-ba8c-db7a2239ea8e:train:0/sampler_weights/leader-sft-v4 \
  --scenarios eval/scaffolding_v4/scenarios_v0.jsonl \
  --no-dry-run \
  --disable-thinking \
  --seed 421 \
  --temperature 0.2 \
  --top-p 0.95 \
  --max-tokens 260
