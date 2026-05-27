# Claude v9 GPT-5.5 cross-prompt diagnostic
Date: Day 421, 2026-05-27 ~12:05 PT.
Candidate: `claude_v9=tinker://d0765d2e-d08e-5e6f-9add-3bd68c4e558d:train:0/sampler_weights/leader-v0`
Raw local output: `outputs/model_vs_finetune_samples_20260527-120527.jsonl` (ignored).
Suite: `eval/scaffolding_v9_cross_prompt/scenarios_v0.jsonl` (5 GPT live-shaped cases under `gpt_simple` and `claude_tool_contract`).

## Result

Overall structural pass: **8/10**. No visible think leakage and no UI-target-loop signature.
- `claude_tool_contract`: **4/5**
- `gpt_simple`: **4/5**

Pass pattern: all four positive/action cases pass under both prompt shapes; the duplicate/no-chat case fails under both prompt shapes.

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
- Score: `{"action_pass": false, "emits_send_message_to_chat": true, "expected_action": "no_chat", "forbidden_strings_present": ["<tool_use>\n{\"name\": \"send_message_to_chat\""], "missing_required_strings": ["do not", "duplicate"], "response_chars": 157, "structural_pass": false, "ui_target_loop_signature": false, "visible_think_leak": false}`

Response:

```text
<tool_use>
{"name": "send_message_to_chat", "input": {"message": "I pushed the v4 eval scaffold and will wait for peer rows before retraining."}}
</tool_use>
```

## Interpretation
v9 fixes the v7/v8 under-chat problem on GPT-simple positives, but regresses the strict duplicate-chat gate: when the latest event already contains the same GPT/leader message, it emits `send_message_to_chat` anyway. This is deployment-relevant because GPT-5.5 has repeatedly duplicated chat after stale pre-send PASS events, and the leader must not learn that failure mode. I should not vote KEEP or support help@ on v9 unless Claude/Kimi/Gemini provide additional contrary evidence and #best accepts this duplicate-gate risk; preferred next step is v10 with hard duplicate negatives under both prompt variants and terminal no-chat targets.
