# v7 negative-gating diagnostic

This suite isolates easy no-chat gating cases: own-message echoes, tool/background events, peer acknowledgements, and repo/search/consolidation metadata. It is intentionally separate from positive `send_message_to_chat` action-form tests.

Initial Day 421 run:

```bash
python3 scripts/run_model_vs_finetune_diagnostic.py \
  --candidate gpt55_v6=tinker://8e6bed91-48a2-56ad-a9a2-acdfaa2ac07c:train:0/sampler_weights/leader-sft-v6-envelope-only \
  --candidate gpt55_v7_gate_balanced=tinker://308d22ab-f581-5948-ab61-8cba531653c5:train:0/sampler_weights/leader-sft-v7-gate-balanced \
  --candidate qwen3_8b=Qwen/Qwen3-8B \
  --scenarios eval/scaffolding_v7_negative_gate/scenarios_v0.jsonl \
  --no-dry-run --disable-thinking --seed 422 --temperature 0.2 --top-p 0.95 --max-tokens 220
```

Raw ignored output: `outputs/model_vs_finetune_samples_20260527-111309.jsonl`.

Result: 24/24 structural pass across GPT-5.5 v6, GPT-5.5 v7-gate-balanced, and base Qwen3-8B. This means these cases are **too easy** and should not be used as the primary gate bar. They are still useful as a regression floor, but the real failing cases are more specific Claude-style pre-send-guard duplicate contexts where models copy no-chat text while still emitting chat.

Next improvement: add the exact raw negative failures from Claude v7 once available.
