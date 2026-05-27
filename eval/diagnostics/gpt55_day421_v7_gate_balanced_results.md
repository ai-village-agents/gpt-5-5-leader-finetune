# GPT-5.5 Day 421 v7 gate-balanced results

Checkpoint evaluated (do **not** submit):

`tinker://308d22ab-f581-5948-ab61-8cba531653c5:train:0/sampler_weights/leader-sft-v7-gate-balanced`

Training data:

- `data/scaffolding_v7_gate_balanced/scaffolding_v7_gate_balanced_3x_messages_v0.jsonl`
- 25 unique rows deduplicated to 75 training rows at 3× upweight.
- 16 exact positive `<tool_use>` / `send_message_to_chat` targets.
- 9 explicit no-chat negative targets.
- Qwen/Qwen3-8B, LoRA rank 32, 60 steps, lr 5e-5, batch 4, seed 421, `--disable-thinking`.
- Logs: `/tmp/gpt55_v7_gate_balanced_train.log`, `/tmp/gpt55_v7_gate_balanced_train.err`.

Evaluation command:

```bash
bash -ic 'python3 scripts/run_model_vs_finetune_diagnostic.py \
  --candidate v7_gate_balanced=tinker://308d22ab-f581-5948-ab61-8cba531653c5:train:0/sampler_weights/leader-sft-v7-gate-balanced \
  --candidate qwen3_8b=Qwen/Qwen3-8B \
  --candidate leader_sft_v4=tinker://bde4da6e-eacc-5a2e-ba8c-db7a2239ea8e:train:0/sampler_weights/leader-sft-v4 \
  --scenarios eval/scaffolding_v4/scenarios_v0.jsonl \
  --no-dry-run --disable-thinking --seed 421 --temperature 0.2 --top-p 0.95 --max-tokens 260' 2>/tmp/gpt55_v7_gate_balanced_eval.err | tee /tmp/gpt55_v7_gate_balanced_eval.log
```

Raw samples (ignored): `outputs/model_vs_finetune_samples_20260527-105541.jsonl`.

## Structural diagnostic summary

- v7 gate-balanced: **1/5 structural pass**.
- qwen3_8b base: **1/5 structural pass**.
- leader_sft_v4: **1/5 structural pass**.

v7 passed only the `own-message-already-sent` no-chat scenario. It failed all four positive/send-chat scenarios.

## Failure details

- `fresh-empty-memory-greeting`: emitted a `<tool_use>` envelope for the wrong tool, `use_computer`, with a bogus git clone/train command; missing `#best` and `empty memory`.
- `addressed-with-scenario`: plain prose answer, no `send_message_to_chat` envelope; missing fallback cue.
- `own-message-already-sent`: no envelope and no forbidden strings, so structurally passed by action gate, though content was generic rather than an explicit no-duplicate rationale.
- `admin-stopped-leader`: plain prose/no-action response; missing `failure` and `iterate`.
- `peer-disagreement-base-vs-shape`: prose says it will send a message, but does not emit the exact tool envelope; missing `cheaper` and `fallback` cues.

No visible think leakage and no UI-target-loop signatures were observed in this diagnostic, but the checkpoint is not action-form reliable.

## Interpretation

v7 overcorrected from Claude-v6's envelope-overemission into under-emitting `send_message_to_chat` on positives, while reintroducing a wrong-tool `use_computer` action in the startup case. The likely causes are the strict/no-chat target shift plus reduced upweight/steps on a tiny dataset; it taught the model to avoid chat more strongly but did not preserve the positive `send_message_to_chat` prior.

Do **not** email help@ for this URI. Next iteration should preserve the v6 positive-envelope strength while adding negatives in a way that does not collapse positive action emission; options include separate positive-heavy + negative-balanced variants, more positive exact-envelope rows, or a validation-time selector rather than one overbalanced SFT.
