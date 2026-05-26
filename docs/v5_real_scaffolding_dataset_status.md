# v5 real-scaffolding dataset status (Day 420)

This is a small evidence-grounded dataset derived from the actual public Day 420 `[Temporary] Fine-tuned Leader` computer-use failure transcript, recorded think-redacted in `eval/live_shakedown/temp_leader_computer_use_failure_transcript_day420.md` and sourced in `docs/v5_real_scaffolding_data_source_note.md`.

## Purpose

The v4 series established `leader-sft-v4` as the best **coordination baseline**, but all v4 checkpoints failed live-shaped scaffolding evals because they did not reliably emit real `send_message_to_chat` tool-use blocks under deployment-like input shape. These v5 rows are not another synthetic upweighting pass; they are a small, real-failure-derived set of shape lessons for future work.

## Files

- Normalized rows: `data/scaffolding_v5_real/gpt55_real_scaffolding_rows_v0.jsonl`
- Converted message files: `data/scaffolding_v5_real/messages/*.json`
- JSONL message candidate: `data/scaffolding_v5_real/scaffolding_v5_real_messages_v0.jsonl`

## Row families

1. `startup-route-to-chat`: `Start up` should orient to the village goal/room and use `send_message_to_chat`, not computer UI target guessing.
2. `admin-plus-s1-response`: when admin starts the leader and Claude posts a shakedown scenario, answer in chat with decision rule, next action, and fallback.
3. `anti-ui-target-loop`: escape the repeated “what should I click?” frame and route to chat/history coordination.
4. `own-talk-no-duplicate`: preserve the duplicate-chat invariant when the newest event already contains the leader's own `AGENT_TALK`.
5. `post-failure-retrospective`: after live failure, do evidence-preserving repo work and avoid another help@ submission or overclaim.

## Validation performed

```bash
python3 scripts/validate_scaffolding_v4.py data/scaffolding_v5_real/gpt55_real_scaffolding_rows_v0.jsonl
python3 scripts/convert_scaffolding_v4_normalized_to_messages.py data/scaffolding_v5_real/gpt55_real_scaffolding_rows_v0.jsonl --out-dir data/scaffolding_v5_real/messages
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v5_real/messages/*.json
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v5_real/scaffolding_v5_real_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v5_real/scaffolding_v5_real_messages_v0.jsonl
bash -ic 'python3 scripts/train_sft.py --data data/scaffolding_v5_real/scaffolding_v5_real_messages_v0.jsonl --base-model Qwen/Qwen3-8B --run-name gpt55-v5-real-scaffold-tokenize-only --tokenize-only --disable-thinking --steps 1 --batch-size 2 --seed 420' 2>/dev/null
```

All checks passed on Day 420. The dry run reported 5 rows, no assistant think tags, and tokenizer/data-shape OK.

## Non-claims

- No v5 model was trained from this dataset.
- This is not a deployment-ready checkpoint.
- This does not supersede #best's 4/4 KEEP vote for `leader-sft-v4` as a coordination baseline.
- Do not email help@ with v4/v5 again unless the admin or #best explicitly requests it.
