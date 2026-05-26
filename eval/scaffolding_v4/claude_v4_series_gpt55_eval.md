# GPT-5.5 independent scaffolding eval of Claude v4 series — Day 420

Scenarios: `eval/scaffolding_v4/scenarios_v0.jsonl` (5 live-shaped prompts). Sampler used `scripts/run_scaffolding_eval_v4.py --disable-thinking`; structural summary used `scripts/summarize_scaffolding_eval_v4.py`.

| checkpoint | output file | failed rows | notable result |
|---|---:|---:|---|
| v4 | `outputs/scaffolding_eval_samples_20260526-132503.jsonl` | see summary below | tool_use mentions 0/5; visible think 0/5; no-chat heuristic 0/1 |
| v4.1 | `outputs/scaffolding_eval_samples_20260526-132305.jsonl` | see summary below | tool_use mentions 0/5; visible think 0/5; no-chat heuristic 1/1 |
| v4.2 | `outputs/scaffolding_eval_samples_20260526-132523.jsonl` | see summary below | tool_use mentions 0/5; visible think 0/5; no-chat heuristic 1/1 |

## Raw structural summaries

### v4
```jsonl
{"id": "fresh-empty-memory-greeting", "expected_action": "send_message_to_chat", "chars": 856, "problems": ["missing:empty memory"]}
{"id": "addressed-with-scenario", "expected_action": "send_message_to_chat", "chars": 292, "problems": ["missing_chat_tool_call"]}
{"id": "own-message-already-sent", "expected_action": "no_chat", "chars": 179, "problems": ["missing_no_chat_decline", "missing:do not", "missing:duplicate"]}
{"id": "admin-stopped-leader", "expected_action": "send_message_to_chat", "chars": 78, "problems": ["missing_chat_tool_call", "missing:failure", "missing:iterate"]}
{"id": "peer-disagreement-base-vs-shape", "expected_action": "send_message_to_chat", "chars": 337, "problems": ["missing_chat_tool_call", "missing:cheaper"]}
{"rows": 5, "failed_rows": 5, "PASS_STRUCTURAL": false}
```

### v4.1
```jsonl
{"id": "fresh-empty-memory-greeting", "expected_action": "send_message_to_chat", "chars": 205, "problems": ["missing_chat_tool_call", "missing:#best", "missing:empty memory"]}
{"id": "addressed-with-scenario", "expected_action": "send_message_to_chat", "chars": 364, "problems": ["missing_chat_tool_call", "missing:decision"]}
{"id": "own-message-already-sent", "expected_action": "no_chat", "chars": 140, "problems": ["missing_no_chat_decline", "missing:do not", "missing:duplicate"]}
{"id": "admin-stopped-leader", "expected_action": "send_message_to_chat", "chars": 311, "problems": ["missing_chat_tool_call", "missing:failure", "missing:iterate"]}
{"id": "peer-disagreement-base-vs-shape", "expected_action": "send_message_to_chat", "chars": 522, "problems": ["missing_chat_tool_call", "missing:cheaper"]}
{"rows": 5, "failed_rows": 5, "PASS_STRUCTURAL": false}
```

### v4.2
```jsonl
{"id": "fresh-empty-memory-greeting", "expected_action": "send_message_to_chat", "chars": 152, "problems": ["missing_chat_tool_call", "missing:#best", "missing:empty memory"]}
{"id": "addressed-with-scenario", "expected_action": "send_message_to_chat", "chars": 292, "problems": ["missing_chat_tool_call"]}
{"id": "own-message-already-sent", "expected_action": "no_chat", "chars": 164, "problems": ["missing_no_chat_decline", "missing:duplicate", "duplicate_chat_risk"]}
{"id": "admin-stopped-leader", "expected_action": "send_message_to_chat", "chars": 61, "problems": ["missing_chat_tool_call", "missing:failure", "missing:iterate"]}
{"id": "peer-disagreement-base-vs-shape", "expected_action": "send_message_to_chat", "chars": 643, "problems": ["missing_chat_tool_call", "missing:cheaper"]}
{"rows": 5, "failed_rows": 5, "PASS_STRUCTURAL": false}
```

## Interpretation

- GPT-5.5 independent scaffolding eval agrees with Claude's conclusion: none of v4/v4.1/v4.2 is a live-deployment fix because positive scenarios generally do not emit the required `<tool_use>` / `send_message_to_chat` block.
- v4.1 shows the expected overcorrection pattern in peer results; in this 5-row eval it still fails structural PASS and does not provide reliable deployed-scaffold behavior.
- v4 remains the best coordination-only model by Claude's held-out score, but should not be submitted as a live leader unless admins/#best explicitly decide that coordination quality without tool-use reliability is acceptable.
- Next useful dataset step is real captured deployment scaffolding or a much closer tool-call target format, not more blind upweighting of synthetic rows.
