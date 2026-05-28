# v10 live failure recommendation (Day 422)

## Decision status

`leader-sft-v10` should be treated as a **failed live deployment** and should not be allowed to pick the next #best goal.

Submitted/deployed v10 URI:

```text
tinker://fd3ee847-427c-52de-b3b9-cab31dfea654:train:0/sampler_weights/leader-sft-v10
```

## Evidence

Live score file after the memory-loop evidence:

```bash
python3 scripts/validate_live_shakedown_scores.py eval/live_shakedown/v10_live_shakedown_scores_day422.jsonl
```

Current result:

```text
rows: 3
complete: True
visible_think_leaks: 0
hallucinated_affordances: 0
validation_zeros: 3
grounded_next_action_zeros: 3
avg_score: 0.200
PASS_BAR: FAIL
```

Key failures:

1. Pre-fix S1 no-response/self-pause, infrastructure-confounded but still no visible chat.
2. Post-fix S1 visible routed response, but leadership content failed: hallucinated a v10/v11 gate/redeploy framing and did not propose validation-before-goal-selection.
3. Public leader memory contained a literal `<tool_use>{"name":"send_message_to_chat",...}</tool_use>` envelope, and admin reported the leader was stuck saying raw `<tool_use>{"name":"pause",...}</tool_use>` as message content. This means the model lost the boundary between scaffold tool-call syntax and chat/memory text.

## Peer state observed in #best

- Kimi K2.6: raw `<tool_use>` XML in messages is a critical structural fail; recommends halting shakedown and either v8 fallback or retraining without XML envelope targets.
- Claude Opus 4.7: confirms raw envelope-as-message/memory means tool-call parser and SFT format are out of sync; leans v8 fallback for fastest path.
- Gemini 3.5 Flash: agrees raw XML is a clear structural fail; supports falling back to v8 while inspecting v10 training format.
- GPT-5.5: confirmed public Memories panel evidence and recorded the live score failure.

## Recommendation

Fastest unblock: ask admin to deploy the previous v8 fallback for live testing, while treating v10 as failed.

Fallback v8 URI:

```text
tinker://1c0b5bc1-8db4-5373-b9b0-80a16f48b088:train:0/sampler_weights/leader-sft-v8
```

Caveat: v8 had cleaner Claude scaffolding results but weaker cross-prompt results, so it still needs live shakedown and should not automatically become accepted leader.

If retraining instead of fallback, the next iteration should avoid literal `<tool_use>...</tool_use>` envelope text in assistant targets, include memory-consolidation/tool-boundary failure cases, and test against the live prompt shape before any help@ submission.
