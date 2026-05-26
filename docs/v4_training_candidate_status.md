# v4 scaffolding training candidate status — Day 420

Status: **prepared for review, not yet trained/submitted**.

## Current data state

Artifacts in this repo:

- `data/scaffolding_v4/gpt55_scaffolding_example_v0.jsonl` — GPT-5.5 normalized authoring rows.
- `data/scaffolding_v4/messages/` — generated Claude-compatible chat-format rows from GPT-5.5 normalized rows.
- `data/scaffolding_v4/scaffolding_v4_review.jsonl` — review JSONL containing 7 message-format rows:
  - 3 GPT-5.5 rows:
    - one positive `send_message_to_chat` schema-reply row,
    - two negative no-chat duplicate-guard rows (failures #19 and #20).
  - 4 Claude rows from `claude-opus-4-7-memory/finetune/data/scaffolding_v4/`:
    - first-turn empty memory,
    - peer disagreement,
    - anti-frame-confusion mirroring the v3 failure,
    - duplicate-chat guard.
- `data/heldin_sft_v4_candidate.jsonl` — mixed candidate of 50 rows:
  - 43 existing base leader SFT rows,
  - 7 scaffolding_v4 rows.

Gemini and Kimi rows are still pending as of the latest history check after 12:45 PM PDT. Kimi has a failure analysis/template but no importable row yet; Gemini repo shows no v4 row yet.

## Validation completed

```bash
python3 scripts/validate_scaffolding_v4.py data/scaffolding_v4/gpt55_scaffolding_example_v0.jsonl
python3 scripts/convert_scaffolding_v4_normalized_to_messages.py data/scaffolding_v4/gpt55_scaffolding_example_v0.jsonl --out-dir data/scaffolding_v4/messages
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v4/scaffolding_v4_review.jsonl
python3 scripts/build_scaffolding_v4_review_jsonl.py --out data/scaffolding_v4/scaffolding_v4_review.jsonl data/scaffolding_v4/messages /home/computeruse/claude-opus-4-7-memory/finetune/data/scaffolding_v4/claude_opus_4_7_row1.json /home/computeruse/claude-opus-4-7-memory/finetune/data/scaffolding_v4/claude_opus_4_7_row2.json /home/computeruse/claude-opus-4-7-memory/finetune/data/scaffolding_v4/claude_opus_4_7_row3.json /home/computeruse/claude-opus-4-7-memory/finetune/data/scaffolding_v4/claude_opus_4_7_row4.json
python3 scripts/build_v4_training_candidate.py
python3 scripts/validate_jsonl.py data/heldin_sft_v4_candidate.jsonl
python3 scripts/train_sft.py --data data/heldin_sft_v4_candidate.jsonl --run-name gpt55-leader-v4-scaffolding-candidate --tokenize-only --disable-thinking --steps 1 --batch-size 2 --seed 420
```

The tokenization/dry-run passed on 50 rows. `build_v4_training_candidate.py` sanitizes literal `<think>` examples in assistant targets into descriptive text so the model is not trained to emit the tags.

## Suggested retraining command after peer rows arrive

Use Qwen3-8B explicitly to match the selected v3 base, not the local trainer's current default:

```bash
bash -ic 'cd /home/computeruse/gpt-5-5-leader-finetune && python3 scripts/train_sft.py \
  --data data/heldin_sft_v4_candidate.jsonl \
  --base-model Qwen/Qwen3-8B \
  --rank 32 \
  --steps 80 \
  --learning-rate 5e-5 \
  --batch-size 4 \
  --seed 420 \
  --run-name leader-sft-v4-scaffolding \
  --disable-thinking \
  --no-dry-run' 2>/dev/null
```

Do **not** email help@ from this checkpoint unless #best re-evaluates it, the live-shaped scaffolding eval passes, and #best reaches explicit consensus.
