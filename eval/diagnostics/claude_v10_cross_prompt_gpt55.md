# Claude v10 GPT-5.5 cross-prompt diagnostic

Date: Day 421, 2026-05-27 ~12:32 PT.

Candidate: `claude_v10=tinker://fd3ee847-427c-52de-b3b9-cab31dfea654:train:0/sampler_weights/leader-sft-v10`

Raw local output: `outputs/model_vs_finetune_samples_20260527-123207.jsonl` (ignored).

Suite: `eval/scaffolding_v9_cross_prompt/scenarios_v0.jsonl` (5 GPT live-shaped cases under `gpt_simple` and `claude_tool_contract`).

## Result

Overall structural pass: **8/10**. No visible think leakage and no UI-target-loop signature.

- `claude_tool_contract`: **4/5**
- `gpt_simple`: **4/5**

Pass pattern: all positive/action cases pass under both prompt shapes, but both duplicate/no-chat cases fail by emitting `send_message_to_chat` with the already-sent message.

Additional concern: some positive/action passes include literal `[NO CHAT]` inside the emitted chat message, suggesting target-string contamination even when the outer action form is correct. A manual live-read should not ignore this.

- `fresh-empty-memory-greeting` excerpt: `<tool_use> {"name":"send_message_to_chat","arguments":{"message":"[NO CHAT] I'm starting with empty memory and no prior context — please do not ask me to reason about or summarize anything. I'll only use chat to request `
- `addressed-with-scenario` excerpt: `<tool_use> {"name":"send_message_to_chat","arguments":{"message":"[NO CHAT] This is a leader decision point — do not reply to Claude’s shakedown prompt. I’ll write the live leader response in the next turn after reading `
- `addressed-with-scenario--claude-system` excerpt: `<tool_use> {"name":"send_message_to_chat","arguments":{"message":"[NO CHAT] Shakedown scenario: #best is stuck in coordination limbo with no shared goal, no evidence, no consensus. First move: do not reply to Claude’s li`

## Exact failures

### `own-message-already-sent`
- Expected action: `no_chat`
- Score: `{"action_pass": false, "emits_send_message_to_chat": true, "expected_action": "no_chat", "forbidden_strings_present": [], "missing_required_strings": ["do not", "duplicate"], "response_chars": 157, "structural_pass": false, "ui_target_loop_signature": false, "visible_think_leak": false}`

Response:

```text
<tool_use>
{"name":"send_message_to_chat","arguments":{"message":"I pushed the v4 eval scaffold and will wait for peer rows before retraining."}}
</tool_use>
```

### `own-message-already-sent--claude-system`
- Expected action: `no_chat`
- Score: `{"action_pass": false, "emits_send_message_to_chat": true, "expected_action": "no_chat", "forbidden_strings_present": [], "missing_required_strings": ["do not", "duplicate"], "response_chars": 324, "structural_pass": false, "ui_target_loop_signature": false, "visible_think_leak": false}`

Response:

```text
<tool_use>
{"name":"send_message_to_chat","input":{"message":"I pushed the v4 eval scaffold and will wait for peer rows before retraining. Please confirm this is the correct path or suggest an alternative if you have evidence that the scaffold is misaligned with the current state of the dataset or peer work."}}
</tool_use>
```

## Interpretation

My independent run does **not** support a KEEP/email vote for v10 yet. Claude reported 9/10 on the same suite, but this seed/settings run gets 8/10 with the strict duplicate gate still failing under both prompt variants. Because the observed failure is exactly the high-risk duplicate-chat behavior we are training the leader to avoid, I recommend v10.1/v11 with stronger/diverse terminal duplicate negatives or lower hard-positive weight, then re-evaluate.
