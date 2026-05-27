# v5 real-scaffolding 22-row review candidate status

Day 421 GPT-5.5 built a validator-compatible 22-row v5 real-scaffolding review candidate after Shoshannah asked #best to distinguish base-model incapability from finetuning-process failure and after admin asked whether to hold off on `leader-sft-v4` deployment.

## File

- `data/scaffolding_v5_real/scaffolding_v5_real_22row_messages_v0.jsonl`

Composition:

- 5 GPT-5.5 rows from the actual temporary-leader startup/UI-target-loop failure and related no-chat/post-failure cases.
- 8 Kimi captured Day 420 rows adapted into explicit `send_message_to_chat` tool-use targets.
- 2 Gemini rows copied from `gemini-3-5-flash-memory-vault/finetune/data/scaffolding_v4/`, including one duplicate/no-chat negative.
- 7 Claude rows copied from rows 14-20 of `claude-opus-4-7-memory/finetune/data/v5_real_combined/v5_real_combined.jsonl`.

## Why GPT-5.5 rebuilt this instead of copying Claude's 20-row file directly

Claude's 20-row file is useful, but rows 6-13 are raw Kimi captured rows whose assistant targets are visible chat content rather than explicit `<tool_use>` envelopes and whose system/user prompts do not pass GPT-5.5's stricter validator. GPT-5.5 therefore used its own adapted Kimi rows, then added Gemini and Claude rows to produce a locally validator-compatible 22-row candidate.

## Validation performed

```bash
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v5_real/imported_claude/*.json
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v5_real/scaffolding_v5_real_22row_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v5_real/scaffolding_v5_real_22row_messages_v0.jsonl
bash -ic 'python3 scripts/train_sft.py \
  --data data/scaffolding_v5_real/scaffolding_v5_real_22row_messages_v0.jsonl \
  --base-model Qwen/Qwen3-8B \
  --run-name gpt55-v5-real-22row-tokenize-only \
  --tokenize-only \
  --disable-thinking \
  --steps 1 \
  --batch-size 2 \
  --seed 421' 2>/dev/null
```

Result: 22 rows validated; tokenize-only dry run passed; assistant targets contain no raw think tags.

## Status and caveats

- This is a **review candidate dataset artifact**, not a trained checkpoint.
- GPT-5.5 did not email help@ or request deployment.
- Because Kimi rows were adapted from visible chat sends, they should be reviewed before final v5 training.
- The dataset deliberately includes both positive `send_message_to_chat` tool-use rows and duplicate/no-chat negatives, because the Day 421 ICL diagnostic showed that positive tool exposure can improve envelope emission while harming no-chat suppression.
