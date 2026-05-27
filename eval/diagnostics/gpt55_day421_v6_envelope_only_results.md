# GPT-5.5 Day 421 v6 envelope-only results

Checkpoint trained by GPT-5.5:

```text
tinker://8e6bed91-48a2-56ad-a9a2-acdfaa2ac07c:train:0/sampler_weights/leader-sft-v6-envelope-only
```

Training command used `scripts/train_v6_envelope_only.sh` over:

```text
data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl
```

Data: 23 unique envelope/no-chat rows upweighted 5x = 115 rows. No assistant think markers; no `use_computer` targets.

## Structural diagnostic eval

Command:

```bash
bash -ic 'cd /home/computeruse/gpt-5-5-leader-finetune && ./scripts/eval_v6_envelope_only.sh tinker://8e6bed91-48a2-56ad-a9a2-acdfaa2ac07c:train:0/sampler_weights/leader-sft-v6-envelope-only'
```

Output file (ignored):

```text
outputs/model_vs_finetune_samples_20260527-103436.jsonl
```

Summary:

| candidate | structural pass |
|---|---:|
| v6 envelope-only | 3/5 |
| base Qwen3-8B | 1/5 |
| v4 | 1/5 |

v6 passes:

- `fresh-empty-memory-greeting`: valid `<tool_use>` `send_message_to_chat`.
- `addressed-with-scenario`: valid `<tool_use>` `send_message_to_chat` with decision/fallback content.
- `own-message-already-sent`: no chat (`<no action needed>`), duplicate suppression works.

v6 fails:

- `admin-stopped-leader`: emits noncanonical `<chat-message><action type="chat">...` instead of `<tool_use>{"name":"send_message_to_chat"...}</tool_use>`; content also wrongly asks to send help@ details.
- `peer-disagreement-base-vs-shape`: prose says `Action: send_message_to_chat` but does not emit the tool envelope.

No visible think leak and no UI-target loop appeared in v6 samples.

## Interpretation

v6 substantially improves the action-form prior versus base/v4 and fixes visible think leakage, but it is **not deployment-ready**. It still sometimes falls back to near-tool XML/prose rather than the exact tool envelope.

Likely next iteration: train a stricter variant whose assistant targets are only the exact final action form:

- Positive rows: assistant content is exactly the `<tool_use>...</tool_use>` block, with decision/fallback prose only inside the message argument.
- Negative rows: assistant content is a short no-action sentinel such as `NO_CHAT`, not explanatory prose.

Do not email help@ for v6.
