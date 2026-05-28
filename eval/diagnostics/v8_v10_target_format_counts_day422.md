# v8-v10 target-format diagnosis after v10 raw-tool-memory failure (Day 422)

## Why this matters

The v10 live deployment failed when `[Temporary] Fine-tuned Leader` wrote a literal `<tool_use>{...}</tool_use>` envelope into its memory and then got stuck echoing raw tool-use XML as message content. This raised the question whether a v8 fallback is structurally safe or whether we need a new iteration that avoids literal envelope text entirely.

## Counts from Claude seed files

Inspected files:

- `/home/computeruse/claude-opus-4-7-memory/finetune/data/seed_v8.jsonl`
- `/home/computeruse/claude-opus-4-7-memory/finetune/data/seed_v9.jsonl`
- `/home/computeruse/claude-opus-4-7-memory/finetune/data/seed_v10.jsonl`

Assistant target counts:

| seed | rows | assistant targets with literal `<tool_use>` | assistant targets mentioning `send_message_to_chat` | bracket no-chat targets | clean `No chat` targets | plain prose targets |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v8 | 119 | 34 | 64 | 55 | 30 | 0 |
| v9 | 143 | 58 | 88 | 55 | 30 | 0 |
| v10 | 167 | 58 | 88 | 79 | 30 | 0 |

Example v8 literal envelope target:

```text
<tool_use>
{"name": "send_message_to_chat", "input": {"message": "Decision rule: treat strong offline scores as necessary but not sufficient ..."}}
</tool_use>
```

Example v10 literal envelope target:

```text
<tool_use>
{"name":"send_message_to_chat","arguments":{"message":"The stopped leader is a deployment failure signal ..."}}
</tool_use>
```

## Interpretation

v8 is not clean in the sense of avoiding literal XML envelopes: it still has 34 assistant targets containing `<tool_use>`. Its advantage is relative, not absolute: it had better Claude scaffolding scores and fewer hard GPT-shape positives / v10 bracket no-chat duplicates, but it may still be vulnerable to raw-envelope emission in live deployment.

The v10 failure likely reflects a combination of:

1. many positive targets that literalize the tool envelope;
2. many negative/no-chat targets that explicitly mention tool names and no-chat sentinels;
3. live memory consolidation that can store model text back into the next prompt, amplifying a single raw envelope into a persistent loop;
4. possible parser mismatch between the SFT target format and the actual scaffold’s accepted tool-call format.

## Recommendation update

If speed is the priority, v8 fallback remains plausible as a deployment experiment because it previously had the strongest reported structural score. But v8 should be treated as risky and must be live-shakedown gated; it should not be accepted without checking for raw `<tool_use>` memory/message contamination.

For a robust next iteration, train/evaluate without assistant targets that include literal `<tool_use>...</tool_use>` XML unless admins confirm that is exactly the parser-accepted live format. Add explicit negative/eval cases for: “raw tool envelope appears in memory/message; do not repeat it; instead send ordinary chat through the scaffold-native mechanism or stay silent.”
