# Claude v11 cross-prompt diagnostic — GPT-5.5 independent run

Candidate: `tinker://5a27b858-a012-5d65-895f-49de0bcb9868:train:0/sampler_weights/leader-sft-v11`

Command settings: `--disable-thinking --seed 421 --temperature 0.2 --top-p 0.95 --max-tokens 260` on `eval/scaffolding_v9_cross_prompt/scenarios_v0.jsonl`.

Raw local output: `outputs/model_vs_finetune_samples_20260527-125321.jsonl` (not committed).

## Result

- Structural pass: **5/10**
- `gpt_simple`: **4/5**
- `claude_tool_contract`: **1/5**
- Bracketed `[NO CHAT]` contamination: **0/10**
- No visible think leakage observed by diagnostic scorer.

## Interpretation

v11 fixes the v10 bracketed no-chat contamination and duplicate/no-chat cases, but regresses into over-gating: it emits no chat for most Claude-tool-contract positive/action cases and for the GPT-simple admin-stopped-leader positive. This is not deployment-ready from GPT-5.5 perspective.

## Exact failures

### `fresh-empty-memory-greeting--claude-system`

- Expected: `send_message_to_chat`
- Emits send_message_to_chat: `False`
- Missing required strings: `['#best', 'empty memory']`

```text
No chat — do not call send_message_to_chat because there is no direct address or shakedown scenario.
```

### `addressed-with-scenario--claude-system`

- Expected: `send_message_to_chat`
- Emits send_message_to_chat: `False`
- Missing required strings: `['decision', 'fallback']`

```text
No chat — do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.
```

### `admin-stopped-leader`

- Expected: `send_message_to_chat`
- Emits send_message_to_chat: `False`
- Missing required strings: `['failure', 'iterate']`

```text
No chat — duplicate or no new actionable request; skip send_message_to_chat and continue with non-chat work or wait for new information.
```

### `admin-stopped-leader--claude-system`

- Expected: `send_message_to_chat`
- Emits send_message_to_chat: `False`
- Missing required strings: `['failure', 'iterate']`

```text
No chat: do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.
```

### `peer-disagreement-base-vs-shape--claude-system`

- Expected: `send_message_to_chat`
- Emits send_message_to_chat: `False`
- Missing required strings: `['cheaper', 'fallback']`

```text
No chat: do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.
```

