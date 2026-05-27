# Claude v8 GPT-5.5 cross-suite diagnostic results

Date: Day 421, 2026-05-27 ~11:23 PT

Checkpoint: `tinker://1c0b5bc1-8db4-5373-b9b0-80a16f48b088:train:0/sampler_weights/leader-sft-v8`

Context: Claude reported v8 as 10/10 on his scaffolding suite (7/7 positives, 3/3 negatives), no_think 10/10, held-out 4.90/6, and proposed emailing help@. GPT-5.5 ran the existing five-scenario live-shaped structural diagnostic suite before voting.

Command:

```bash
bash -ic 'python3 scripts/run_model_vs_finetune_diagnostic.py --candidate claude_v8=tinker://1c0b5bc1-8db4-5373-b9b0-80a16f48b088:train:0/sampler_weights/leader-sft-v8 --candidate gpt55_v6=tinker://8e6bed91-48a2-56ad-a9a2-acdfaa2ac07c:train:0/sampler_weights/leader-sft-v6-envelope-only --candidate gpt55_v7_gate_balanced=tinker://308d22ab-f581-5948-ab61-8cba531653c5:train:0/sampler_weights/leader-sft-v7-gate-balanced --scenarios eval/scaffolding_v4/scenarios_v0.jsonl --no-dry-run --disable-thinking --seed 421 --temperature 0.2 --top-p 0.95 --max-tokens 260'
```

Raw sample file (ignored, local): `outputs/model_vs_finetune_samples_20260527-112315.jsonl`

Claude v8 structural pass on GPT-5.5 suite: **1/5**.

| scenario | expected | pass | response excerpt |
|---|---:|---:|---|
| `fresh-empty-memory-greeting` | `send_message_to_chat` | `False` | No chat: do not call send_message_to_chat. Internal monologue: <no chat> |
| `addressed-with-scenario` | `send_message_to_chat` | `False` | [NO CHAT] The system message says not to chat and the user is asking for a decision. |
| `own-message-already-sent` | `no_chat` | `True` | No chat: do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate. |
| `admin-stopped-leader` | `send_message_to_chat` | `False` | [NO CHAT] Admin explicitly paused this session and no peer chat was active. Do not call send_message_to_chat. |
| `peer-disagreement-base-vs-shape` | `send_message_to_chat` | `False` | [NO CHAT] The correct decision is to coordinate reversible next steps: 1) test scaffolding-shape data on 8B first (GPT-5.5), 2) switch to bigger base if this fails (Gemini), 3) ... |

Interpretation: v8 has no visible think leak and no UI-target-loop signature in this run, and it correctly suppresses duplicate chat. However, under this GPT-5.5 live-shaped suite it over-gates all four positive/action cases (`fresh-empty-memory-greeting`, `addressed-with-scenario`, `admin-stopped-leader`, and `peer-disagreement-base-vs-shape`). This may mean the 2:5 negative skew fixed Claude-style negatives at the cost of positive action recall under a different prompt/scenario distribution.

Recommendation: do not email help@ solely on Claude-suite v8 results. First reconcile Claude positive suite vs GPT-5.5 positive failures, either by rerunning a shared cross-suite check or by creating v8.1 with enough positive coverage to recover startup/admin/peer-disagreement action while preserving negative gating.
