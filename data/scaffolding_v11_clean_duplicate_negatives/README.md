# GPT-5.5 v11 clean duplicate negatives

Clean variant of the v10 hard duplicate/no-chat rows. The purpose is to preserve the duplicate gate signal while removing bracketed `[NO_CHAT]` / `[NO CHAT]` sentinel tokens that contaminated v10 positive chat messages.

Assistant targets are terminal prose, contain no `<tool_use>` envelope, and explicitly say to skip `send_message_to_chat`:

```text
No chat — duplicate or no new actionable request; skip send_message_to_chat and continue with non-chat work or wait for new information.
```

Files:
- `gpt55_v11_clean_duplicate_negative_8row_messages_v0.jsonl` — 8 unique rows.
- `gpt55_v11_clean_duplicate_negative_3x_messages_v0.jsonl` — 24 rows at 3×.
- `gpt55_v11_clean_duplicate_negative_stats.json` — simple counts.

Recommended use: replace or augment bracketed-prefix duplicate negatives in a v11 mixture; re-run GPT cross-prompt duplicate cases and inspect positive chat content for absence of literal `[NO CHAT]` contamination.
