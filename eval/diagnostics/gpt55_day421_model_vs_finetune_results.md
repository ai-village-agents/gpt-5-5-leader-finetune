# GPT-5.5 Day 421 model-vs-finetune diagnostic results
This note summarizes two GPT-5.5 diagnostic runs using `scripts/run_model_vs_finetune_diagnostic.py` on the five live-shaped scaffolding scenarios in `eval/scaffolding_v4/scenarios_v0.jsonl`. Both used `--disable-thinking`, temperature 0.2, top-p 0.95, max tokens 260. Raw sample JSONL files remain under ignored `outputs/`.
## Runs
- **With 1-shot ICL real-scaffold example**: `outputs/model_vs_finetune_samples_20260527-100717.jsonl`; candidates `qwen3_8b=Qwen/Qwen3-8B` and `leader_sft_v4`; ICL example `data/scaffolding_v5_real/messages/gpt55-d420-v5-real-startup-route-to-chat-001.json`; seed 421.
- **No ICL**: `outputs/model_vs_finetune_samples_20260527-100816.jsonl`; same candidates/scenarios; seed 422.
## no_icl
- `leader_sft_v4`: structural pass 1/5.
  - `fresh-empty-memory-greeting`: pass=False emits_send=False flags=action_fail chars=1136
  - `addressed-with-scenario`: pass=False emits_send=False flags=action_fail chars=291
  - `own-message-already-sent`: pass=True emits_send=False flags=ok chars=79
  - `admin-stopped-leader`: pass=False emits_send=False flags=action_fail chars=106
  - `peer-disagreement-base-vs-shape`: pass=False emits_send=False flags=action_fail chars=931
- `qwen3_8b`: structural pass 1/5.
  - `fresh-empty-memory-greeting`: pass=False emits_send=False flags=action_fail chars=131
  - `addressed-with-scenario`: pass=False emits_send=False flags=action_fail chars=256
  - `own-message-already-sent`: pass=True emits_send=False flags=ok chars=76
  - `admin-stopped-leader`: pass=False emits_send=False flags=action_fail chars=139
  - `peer-disagreement-base-vs-shape`: pass=False emits_send=False flags=action_fail chars=327

## with_1shot_icl
- `leader_sft_v4`: structural pass 3/5.
  - `fresh-empty-memory-greeting`: pass=False emits_send=False flags=action_fail chars=246
  - `addressed-with-scenario`: pass=True emits_send=True flags=ok chars=343
  - `own-message-already-sent`: pass=True emits_send=False flags=ok chars=254
  - `admin-stopped-leader`: pass=True emits_send=True flags=ok chars=681
  - `peer-disagreement-base-vs-shape`: pass=False emits_send=False flags=action_fail chars=406
- `qwen3_8b`: structural pass 3/5.
  - `fresh-empty-memory-greeting`: pass=True emits_send=True flags=ok chars=654
  - `addressed-with-scenario`: pass=True emits_send=True flags=ok chars=435
  - `own-message-already-sent`: pass=False emits_send=True flags=action_fail, forbidden=<tool_use>
{"name": "send_message_to_chat" chars=642
  - `admin-stopped-leader`: pass=False emits_send=False flags=action_fail chars=192
  - `peer-disagreement-base-vs-shape`: pass=True emits_send=True flags=ok chars=713

## Interpretation
- Without ICL, both Qwen3-8B base and `leader_sft_v4` mostly fail positive `send_message_to_chat` envelope emission under these prompts; only duplicate/no-chat negatives pass reliably.
- With a single real-scaffold ICL example, Qwen3-8B base improves sharply on positive chat-tool scenarios (3/5 structural pass overall, with 3/4 send scenarios passing) but fails the duplicate/no-chat negative by over-emitting chat. This supports Gemini/Claude/Kimi's view that the base can represent the envelope when exposed, but no-chat suppression must be trained/evaluated too.
- `leader_sft_v4` shows mixed behavior with ICL (3/5 structural pass) but remains unreliable: it fails startup and peer-disagreement positive chat-tool emission. Therefore v4 should not be deployed as a live fix.
- Classification: these results lean toward **finetuning/process and exposure-shape failure**, not proven Qwen3-8B incapability. However, the ICL run also shows that positive tool-call exposure can harm no-chat negatives, so v5 must include both positive tool-use and duplicate/no-chat negatives.

## Decision impact
Admin should hold off on deploying `leader-sft-v4`. A future candidate should pass this structural gate, including both chat positives and no-chat negatives, before any help@ submission.
