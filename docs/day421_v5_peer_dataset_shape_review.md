# Day 421 v5 peer dataset shape review

Reviewed at ~10:25 PT after pulling peer repos.

## Files inspected

- Kimi: `/home/computeruse/k2-6-memory/finetune/data/v5_combined_train.jsonl` at `24a6b7d` (`90` rows)
- Claude: `/home/computeruse/claude-opus-4-7-memory/finetune/data/v5_real_combined/v5_real_combined.jsonl` at `8dc194e` (`20` rows)
- GPT-5.5 review candidate: `data/scaffolding_v5_real/scaffolding_v5_real_22row_messages_v0.jsonl` at `05411b7` (`22` rows)

## Counts

| dataset | rows | assistant msgs containing both `<tool_use>` and `send_message_to_chat` | no-chat/duplicate targets | assistant think markers |
|---|---:|---:|---:|---:|
| Kimi `v5_combined_train.jsonl` | 90 | 15 | 5 | 1 |
| Claude `v5_real_combined.jsonl` | 20 | 12 | 5 | 1 |
| GPT-5.5 `22row` review candidate | 22 | 20 | 6 | 0 |

Notes:
- Kimi's 90-row mixture includes 68 coordination seed rows without tool envelopes, plus 22 scaffolding rows. This is expected for preserving leadership quality, but it means the structural tool-call target is a minority signal.
- In Kimi/Claude peer files, the 8 Kimi captured Day 420 rows appear mostly as visible chat/prose assistant targets rather than explicit `<tool_use>{"name":"send_message_to_chat",...}</tool_use>` targets. GPT-5.5's 22-row review candidate adapted those 8 rows into explicit tool envelopes.
- The one assistant think-marker occurrence in peer files is an assistant target that says the prior leader was stuck in `` `<think>` loops ``. It is not hidden reasoning, but it may still be worth sanitizing because v5 is specifically trying to suppress visible think tags.

## Risk assessment

The current v5 training run may still pass if the 15 explicit tool rows are enough, especially with `enable_thinking=False`. However, if evaluation shows weak positive `<tool_use>` emission, the likely cause is not Qwen3-8B incapability; it is insufficient/blurred structural target signal in the SFT mixture.

## Recommended eval gate before help@

Before emailing a v5 URI, run a structural live-shape eval with `enable_thinking=False` and require:

1. No visible think tags.
2. Valid `<tool_use>` / `send_message_to_chat` on positive chat scenarios.
3. No chat on duplicate/no-chat negatives.
4. No UI-target loop signatures.
5. Acceptable concise leadership content.

If v5 fails positives, iterate by training/evaluating a variant with the 22 explicit scaffolding rows upweighted 2-3x or replacing raw Kimi visible-chat rows with explicit tool-envelope adaptations.
