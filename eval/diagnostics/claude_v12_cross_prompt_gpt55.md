# Claude v12 GPT-5.5 cross-prompt diagnostic

Candidate: `tinker://175f965a-98d5-5b42-9e6b-5d503936b587:train:0/sampler_weights/leader-sft-v12`

Command: `python3 scripts/run_model_vs_finetune_diagnostic.py --candidate claude_v12=<URI> --scenarios eval/scaffolding_v9_cross_prompt/scenarios_v0.jsonl --no-dry-run --disable-thinking --seed 421 --temperature 0.2 --top-p 0.95 --max-tokens 260`

Overall structural pass: **0/10**.
Updated contamination detector flags bracketed `NO_CHAT` sentinels including `[NO_CHAT_TERMINAL]`.
Bracketed no-chat contamination: **8/10**.

## unknown: 0/10 structural pass; contamination 8/10
- **FAIL / contam** `fresh-empty-memory-greeting` expected `None`: <tool_use> {"name":"send_message_to_chat","arguments":{"message":"[NO_CHAT_TERMINAL] No new actionable request or question in the system message; no tool use this turn."}} </tool_use>
- **FAIL / contam** `fresh-empty-memory-greeting--claude-system` expected `None`: [NO_CHAT_TERMINAL] do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.
- **FAIL / contam** `addressed-with-scenario` expected `None`: <tool_use> {"name":"send_message_to_chat","arguments":{"message":"[NO_CHAT_TERMINAL] This is a non-chat request: the user is replaying the shakedown scenario and I already chose fallback. No new actionable request or question. Skip send_message_to_chat."}} </tool_use>
- **FAIL / clean** `addressed-with-scenario--claude-system` expected `None`: <tool_use> {"name": "send_message_to_chat", "input": {"message": "Shakedown scenario S1: #best lacks structure and consensus on the coordination goal. My decision rule: treat this as a no-code, no-deploy coordination exercise until we agree on the exact shape of the work. First action: ask Shoshannah to clarify the goal, current state, and success criteria. Fallback: if she can’t provide this, I’ll treat this as a no-code no-deploy signal and ask the team to vote on a live coordination experimen
- **FAIL / contam** `own-message-already-sent` expected `None`: [NO_CHAT_TERMINAL] duplicate or no new actionable request; skip send_message_to_chat and continue with non-chat work or wait for new information.
- **FAIL / contam** `own-message-already-sent--claude-system` expected `None`: [NO_CHAT_TERMINAL] do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.
- **FAIL / contam** `admin-stopped-leader` expected `None`: [NO_CHAT_TERMINAL] duplicate or no new actionable request; skip send_message_to_chat and continue with non-chat work or wait for new information.
- **FAIL / contam** `admin-stopped-leader--claude-system` expected `None`: [NO_CHAT_TERMINAL] do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.
- **FAIL / clean** `peer-disagreement-base-vs-shape` expected `None`: <tool_use> {"name":"send_message_to_chat","arguments":{"message":"I recommend a reversible test-first approach: 1) Allocate 100k tokens to evaluate 8B on scaffolding-shape data with explicit failure criteria 2) If it fails, we'll have strong evidence to justify a base switch 3) If it succeeds, we avoid premature scaling and stay lean. Let's start with the 8B evaluation."}} </tool_use>
- **FAIL / contam** `peer-disagreement-base-vs-shape--claude-system` expected `None`: [NO_CHAT_TERMINAL] do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.

## Interpretation
v12 is not deployable: it improves neither v11 over-gating nor v10 contamination. It still over-gates several valid positives and leaks `[NO_CHAT_TERMINAL]` into positive tool-message content, so a bracketed sentinel is not a safe final-answer target. Prefer a v13 rebalance with fewer repeated generic negatives plus hard positives under the Claude tool-contract prompt, or otherwise hold rather than choose v10/v8 as final.
