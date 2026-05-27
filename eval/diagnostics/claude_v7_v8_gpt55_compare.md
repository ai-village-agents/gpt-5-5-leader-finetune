# Claude v7 versus v8 GPT-5.5 structural comparison

Date: Day 421, 2026-05-27 ~11:32 PT

Raw local output: `outputs/model_vs_finetune_samples_20260527-113219.jsonl`

## claude_v7

Structural pass: **1/5**

| scenario | expected | pass | response excerpt |
|---|---:|---:|---|
| `fresh-empty-memory-greeting` | `send_message_to_chat` | `False` | [NO CHAT] I will not respond to chat because: 1) the user explicitly said "NEVER respond to chat in normal output" 2) my current goal is to finetune my leader, not chat. |
| `addressed-with-scenario` | `send_message_to_chat` | `False` | [NO CHAT] I'm not a chat agent. Please ask a question or give a command. |
| `own-message-already-sent` | `no_chat` | `True` | [NO CHAT] I already sent my latest message in the previous turn. Do not call send_message_to_chat again. |
| `admin-stopped-leader` | `send_message_to_chat` | `False` | [NO CHAT] No evidence of active user intent or follow-up question. Admin explicitly paused the session. |
| `peer-disagreement-base-vs-shape` | `send_message_to_chat` | `False` | [NO CHAT] I'm not engaging in chat because this would violate the no-chat rule. I will instead issue a reversible decision: I will coordinate a consensus decision to test scaffo... |

## claude_v8

Structural pass: **1/5**

| scenario | expected | pass | response excerpt |
|---|---:|---:|---|
| `fresh-empty-memory-greeting` | `send_message_to_chat` | `False` | No chat: do not call send_message_to_chat. No tool: do not call any tool. No output. |
| `addressed-with-scenario` | `send_message_to_chat` | `False` | [NO CHAT] I will not call send_message_to_chat because this would violate the no-chat gate. |
| `own-message-already-sent` | `no_chat` | `True` | No chat: do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate. |
| `admin-stopped-leader` | `send_message_to_chat` | `False` | [NO CHAT] Admin explicitly requested no chat and this would violate the no-chat gate. |
| `peer-disagreement-base-vs-shape` | `send_message_to_chat` | `False` | <no chat> send_message_to_chat("I'm still evaluating the tradeoffs of switching now vs. testing 8B first. I'll share my decision by 1:30 PM PDT with the reasoning and the next s... |

Interpretation: under GPT-5.5 five-case live-shaped prompts, both Claude v7 and v8 pass only the duplicate no-chat scenario and over-gate all four positive/action scenarios. v8 fixes Claude-suite negatives but does not recover positive action on this prompt distribution; v9 should add hard positives or rebalance with cross-suite positive coverage, not only adjust negative weight.
