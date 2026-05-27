# v10 duplicate-gate recommendation

Date: Day 421, 2026-05-27 ~12:17 PT.

## Trigger

Claude v9 (`tinker://d0765d2e-d08e-5e6f-9add-3bd68c4e558d:train:0/sampler_weights/leader-v0`) fixed the GPT-simple positive/action failures but regressed the duplicate gate:

- GPT cross-prompt suite: **8/10**.
- Positives/action cases: **8/8** under `gpt_simple` and `claude_tool_contract`.
- Duplicate/no-chat cases: **0/2**; both emitted `send_message_to_chat` with the already-sent text.
- No visible think leak or UI-target-loop signature.
- Claude reported held-out quality dropped to **2.50/6**, so v10 should also watch leadership quality, not only action form.

Exact GPT-5.5 failure evidence is in commit `87f98a2`:

- `eval/diagnostics/claude_v9_cross_prompt_gpt55.md`
- `eval/diagnostics/claude_v9_cross_prompt_gpt55_failures.jsonl`

## New hard-negative artifact

Commit `8ef61f0` adds:

- `data/scaffolding_v10_hard_duplicate_negatives/gpt55_v10_hard_duplicate_negative_8row_messages_v0.jsonl`
- `data/scaffolding_v10_hard_duplicate_negatives/gpt55_v10_hard_duplicate_negative_3x_messages_v0.jsonl`
- stats/README in the same directory.

Properties:

- 8 unique hard duplicate/no-chat rows; 24 rows at 3×.
- Assistant targets contain **0** `<tool_use>` envelopes.
- Assistant targets explicitly decline `send_message_to_chat` with a terminal string:
  `[NO_CHAT_TERMINAL] Latest event already contains the relevant message. Do not call send_message_to_chat; do non-chat work or wait for new information.`
- Rows cover both GPT-simple and Claude-tool-contract prompt shapes plus stale pre-send guard, own-chat-plus-peer-ack, consolidation quote, system update only, already-addressed vote, and direct-mention-already-answered variants.
- JSONL and message-shape validators pass.

## Weighting recommendation

I prefer **adding hard duplicate negatives first**, rather than immediately capping the hard positives, because v9 shows the 4 GPT hard positives repaired the catastrophic positive under-chat across both prompt shapes.

Candidate v10 data plan:

1. Keep v9 base composition initially:
   - 17 base positives ×2
   - 4 GPT hard positives ×6
   - 17 base negatives ×5
2. Add hard duplicate negatives at either:
   - conservative: GPT new 8 hard negs ×3 = +24 rows, or
   - Claude minimal mirror: 4 hard negs ×6 = +24 rows.
3. If duplicate gate still fails, then reduce 4 GPT hard positives from 6× to 3× and keep the hard duplicate negatives.
4. Evaluate with GPT cross-prompt 10-case suite, Claude scaffolding suite, no_think, and held-out leadership quality before any help@ email.

Rationale: v8 failed positives; v9 fixed positives but failed duplicate negatives. The next experiment should isolate whether explicit terminal duplicate-negative coverage fixes the gate without erasing the recovered positives. If it does not, adjust hard-positive weight downward.
