# GPT-5.5 v10 hard duplicate negatives

Created Day 421 after Claude v9 passed all 8 cross-prompt positive/action cases but failed both duplicate/no-chat cases by emitting `send_message_to_chat` with the already-sent message.

Files:
- `gpt55_v10_hard_duplicate_negative_8row_messages_v0.jsonl`: 8 unique hard negative message rows.
- `gpt55_v10_hard_duplicate_negative_3x_messages_v0.jsonl`: 24 rows (3× upweight).

Assistant targets intentionally use a terminal no-chat string with no `<tool_use>` envelope and no `<tool_use>` envelope in the assistant content; it explicitly declines `send_message_to_chat` for validator/training clarity:

```text
[NO_CHAT_TERMINAL] Latest event already contains the relevant message. Do not call send_message_to_chat; do non-chat work or wait for new information.
```

Recommended v10 use: keep v9 hard positives because they fixed positives, but add these duplicate negatives under both GPT-simple and Claude-tool-contract prompt shapes; tune weights so positives remain 100% while duplicate/no-chat gate recovers.
