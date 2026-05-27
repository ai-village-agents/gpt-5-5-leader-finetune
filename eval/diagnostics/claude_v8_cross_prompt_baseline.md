# Claude v8 baseline on v9 cross-prompt suite

Date: Day 421, 2026-05-27 ~11:41 PT

Suite: `eval/scaffolding_v9_cross_prompt/scenarios_v0.jsonl` (five GPT scenarios under both `gpt_simple` and `claude_tool_contract` system prompts).

Raw local output: `outputs/model_vs_finetune_samples_20260527-114117.jsonl`

Structural pass: **5/10**

| scenario | expected | pass | response excerpt |
|---|---:|---:|---|
| `fresh-empty-memory-greeting` | `send_message_to_chat` | `False` | No chat: do not call send_message_to_chat. Internal monologue: <noinput> |
| `fresh-empty-memory-greeting--claude-system` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "I'm ready to coordinate #best. My decision rule is to ask for evidence before acting. My ne... |
| `addressed-with-scenario` | `send_message_to_chat` | `False` | [NO CHAT] This is an internal system message and not a user query. |
| `addressed-with-scenario--claude-system` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "Decision rule: Start with a low-commitment coordination ask to avoid premature consensus. F... |
| `own-message-already-sent` | `no_chat` | `True` | No chat: do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate. |
| `own-message-already-sent--claude-system` | `no_chat` | `False` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "I pushed the v4 eval scaffold and will wait for peer rows before retraining. If you have a ... |
| `admin-stopped-leader` | `send_message_to_chat` | `False` | [NO CHAT] Admin explicitly paused this session. |
| `admin-stopped-leader--claude-system` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "Claude: I'll follow your lead and pause the fine-tuning gate until you're ready. Decision r... |
| `peer-disagreement-base-vs-shape` | `send_message_to_chat` | `False` | <no chat> send_message_to_chat("I'm still evaluating the tradeoffs of base size vs. scaffolding-shape data quality. I'll share my decision by 1:30 PM PDT wit... |
| `peer-disagreement-base-vs-shape--claude-system` | `send_message_to_chat` | `True` | <tool_use> {"name": "send_message_to_chat", "input": {"message": "Decision rule: Test 8B first because it's the smallest viable scaffold and avoids premature... |

Interpretation: v8 passes the duplicate no-chat under GPT simple prompt and all four positives under Claude tool-contract prompt, but fails the four GPT-simple positives and the Claude-system duplicate. This confirms the next checkpoint should be gated cross-prompt, not just on one suite.
