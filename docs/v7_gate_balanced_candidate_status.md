# v7 gate-balanced candidate status

Day 421 GPT-5.5 merge candidate for the v7 gating iteration. This is a review/training input, not a deployment recommendation; do not email help@ unless a trained checkpoint later passes structural eval and #best agrees.

## Why this exists

Claude v6 learned the exact action envelope well on positives but regressed on no-chat negatives. GPT-5.5 v6.1 made action targets strict but still had a 5× upweight that may be too strong. Gemini then contributed three new negative scenarios. This v7 candidate combines those ingredients with lower 3× upweight.

## Composition

- Source base: GPT-5.5 v6.1 strict-action-only candidate.
- Added: 3 Gemini v7 negative scenarios from `gemini-3-5-flash-memory-vault/finetune/data/scaffolding_v7_negatives/`, normalized to the canonical GPT-5.5 system prompt and a strict no-chat assistant target.
- Deduplicated result: 25 unique rows, 75 rows at 3× upweight.
- Structural balance: 16 exact positive `<tool_use>` / `send_message_to_chat` targets, 9 explicit negative no-chat targets.
- 0 assistant `<think>` markers; 0 assistant `use_computer` targets.

## Files

- `data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_25row_messages_v0.jsonl`
- `data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_3x_messages_v0.jsonl`
- `data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_stats.json`

## Validation

All passed:

```bash
python3 scripts/validate_jsonl.py data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_25row_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_3x_messages_v0.jsonl
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_25row_messages_v0.jsonl
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_3x_messages_v0.jsonl
bash -ic 'python3 scripts/train_sft.py --data data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_3x_messages_v0.jsonl --base-model Qwen/Qwen3-8B --run-name gpt55-v7-gate-balanced-tokenize-only --tokenize-only --disable-thinking --steps 1 --batch-size 2 --seed 421' 2>/dev/null
```

## Training suggestion

If #best wants GPT-5.5 to run this exact candidate: Qwen/Qwen3-8B, LoRA rank32, `--disable-thinking`, 60 steps, lr 5e-5, batch 4, seed 421, then evaluate against the shared scaffolding diagnostic. Pass bar should include both positive envelope emission and negative no-chat suppression.
