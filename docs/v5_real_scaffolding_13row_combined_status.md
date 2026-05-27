# v5 real-scaffolding 13-row combined dataset status

Day 421 GPT-5.5 built a combined real-scaffolding dataset to support the post-Shoshannah diagnostic direction: distinguish base-model incapability from finetuning-process failure, and do not deploy `leader-sft-v4` as a live fix.

## Files

- `data/scaffolding_v5_real/scaffolding_v5_real_13row_messages_v0.jsonl`
  - 13 message-format rows total.
  - 5 GPT-5.5 real-failure-derived rows from `data/scaffolding_v5_real/messages/*.json`.
  - 8 Kimi captured Day 420 rows adapted under `data/scaffolding_v5_real/imported_kimi_tooluse/*.json`.

## Kimi row adaptation

Source rows came from:

```text
/home/computeruse/k2-6-memory/tools/scaffolding_capture/kimi_real_scaffolding_v2.jsonl
```

Those rows contain real event-log/computer-use context and the final chat content that Kimi sent, but the assistant target is the visible chat message rather than the explicit live leader tool-call envelope. For leader SFT, GPT-5.5 adapted each Kimi target into:

```text
Decision Rule: ... use the chat tool ...

<tool_use>
{"name": "send_message_to_chat", "input": {"message": "<captured Kimi chat content>"}}
</tool_use>
```

Other adaptations:

- Replaced the generic Kimi system prompt with a `[Temporary] Fine-tuned Leader` system/tool contract.
- Normalized the event-log phrase to `Here is what has happened since you started your session` for compatibility with existing validators.
- Sanitized literal hidden-reasoning markers in captured discussion text so assistant targets contain no raw `<think>` / `</think>` tags.
- Preserved source event id, session id, and timestamp metadata on each adapted row.

## Validation performed

```bash
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v5_real/imported_kimi_tooluse/*.json
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v5_real/scaffolding_v5_real_13row_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v5_real/scaffolding_v5_real_13row_messages_v0.jsonl
bash -ic 'python3 scripts/train_sft.py \
  --data data/scaffolding_v5_real/scaffolding_v5_real_13row_messages_v0.jsonl \
  --base-model Qwen/Qwen3-8B \
  --run-name gpt55-v5-real-13row-tokenize-only \
  --tokenize-only \
  --disable-thinking \
  --steps 1 \
  --batch-size 2 \
  --seed 421' 2>/dev/null
```

Result: validators passed; dry run reported 13 rows, no assistant think tags, and `DRY RUN OK`.

## Caveats

- This is a **dataset artifact**, not a trained checkpoint.
- No help@ email or deployment request was sent.
- The 8 Kimi rows are adapted from real chat sends; they are not raw live leader tool traces. They are useful because they combine real event-log context with explicit tool-envelope targets, but they should be reviewed before final v5 training.
- Positive `send_message_to_chat` rows must be balanced with duplicate/no-chat negatives; GPT-5.5's Day 421 ICL diagnostic showed that one-shot positive exposure can improve chat-tool emission while harming no-chat suppression.

## Recommended use

Use this 13-row file as one candidate component for a v5 run, ideally combined with Claude's corrected template/data and any Gemini rows, then evaluate with `scripts/run_model_vs_finetune_diagnostic.py` before any admin spinup.
