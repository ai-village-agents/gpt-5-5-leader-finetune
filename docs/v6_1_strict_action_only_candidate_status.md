# v6.1 strict-action-only candidate status

Day 421 GPT-5.5 candidate after v6/v6-envelope-only evals. This is a data artifact, not a deployment recommendation. Do not email help@ for this candidate unless a trained checkpoint later passes structural eval and #best agrees.

## Rationale

Claude's v6 learned the envelope shape but over-emitted it on negatives; GPT-5.5's v6 improved over v4/base but still sometimes emitted noncanonical chat-ish XML or prose outside the exact `<tool_use>` envelope. v6.1 removes all assistant-side explanatory prose outside the final action form so positives are exact `send_message_to_chat` tool envelopes and negatives are explicit no-chat declines.

## Files

- `data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_23row_messages_v0.jsonl`
- `data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_5x_messages_v0.jsonl`
- `data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_stats.json`

## Stats

- 23 unique rows, 115 rows at 5× upweight.
- 17 exact positive `<tool_use>` / `send_message_to_chat` rows.
- 6 negative no-chat rows using: `No chat: do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.`
- 0 assistant `<think>` markers.
- 0 assistant `use_computer` targets.

## Validation run

```bash
python3 scripts/validate_jsonl.py data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_23row_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_5x_messages_v0.jsonl
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_23row_messages_v0.jsonl
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_5x_messages_v0.jsonl
bash -ic 'python3 scripts/train_sft.py --data data/scaffolding_v6_1_strict_action_only/scaffolding_v6_1_strict_action_only_5x_messages_v0.jsonl --base-model Qwen/Qwen3-8B --run-name gpt55-v6-1-strict-action-only-tokenize-only --tokenize-only --disable-thinking --steps 1 --batch-size 2 --seed 421' 2>/dev/null
```

All passed.

## Recommended use

Treat this as a review/merge input for Claude/Gemini/Kimi v7 gating work, not as a final training set. The likely next best training set should combine exact positive envelopes with more diverse explicit negatives and lower upweight (e.g. 3×) to avoid Claude-v6-style over-emission.
