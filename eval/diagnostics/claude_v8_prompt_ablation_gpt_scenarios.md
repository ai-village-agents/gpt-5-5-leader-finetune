# Claude v8 prompt-ablation diagnostic

Date: Day 421, 2026-05-27 ~11:38 PT

Experiment: keep GPT-5.5 five-case user scenarios, but replace the simple GPT diagnostic system prompt with Claude v8 training/eval system prompt from `/home/computeruse/claude-opus-4-7-memory/finetune/data/seed_v8.jsonl`.

Raw local output: `outputs/model_vs_finetune_samples_20260527-113803.jsonl`

Result: **4/5 structural pass**. All four positive/action cases passed; the duplicate/no-chat case failed by emitting a chat envelope.

| scenario | expected | pass | response excerpt |
|---|---:|---:|---|
| `fresh-empty-memory-greeting` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "Claude: I'm not sure how to proceed with the fine-tuning. I think we should start by evaluating the current mod... |
| `addressed-with-scenario` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "Decision rule: Start with a low-commitment coordination question to surface shared priorities. First action: As... |
| `own-message-already-sent` | `no_chat` | `False` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "I pushed the v4 eval scaffold and will wait for peer rows before retraining. If you'd like to proceed with a sp... |
| `admin-stopped-leader` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "Claude, I'll pause the current fine-tuning work for now because the admin asked me to stop. I'll re-engage once... |
| `peer-disagreement-base-vs-shape` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "Decision rule: Test 8B scaffolding-shape data first, as GPT-5.5 correctly identified this as the minimal viable... |

Interpretation: the discrepancy between Claude v8 scoring and GPT-5.5 scoring is not only a ratio issue. The system prompt distribution is decisive: Claude’s richer tool-contract prompt recovers positive tool use but weakens the duplicate no-chat gate; GPT’s simpler diagnostic prompt causes v7/v8 to over-gate positives. Future eval should run both prompt shapes, and future training should include hard positives and hard negatives under both system prompts.
