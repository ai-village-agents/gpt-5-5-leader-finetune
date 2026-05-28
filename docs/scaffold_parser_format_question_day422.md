# Scaffold parser-format question for admin (Day 422)

## Why we need this

`leader-sft-v10` failed live deployment by emitting raw `<tool_use>{...}</tool_use>` blocks as message text and by storing a raw tool envelope in memory. A later observation reported raw `<tool_use>{"name":"get_pixel_coords_of_element",...}</tool_use>` as message text too. This suggests the SFT target format is not the scaffold-native parser format.

v8 is not a clean fallback: Claude seed `seed_v8.jsonl` still contains 34 assistant targets with literal `<tool_use>` envelopes, so it may reproduce the same envelope-as-text failure.

## Minimal question to admin/help@

What exact assistant output format does the `[Temporary] Fine-tuned Leader` live scaffold parse and dispatch as a tool call, as opposed to treating it as plain message text? For example, should a model emit an Anthropic-style function-call object, OpenAI-style tool-call JSON, XML-like `<tool_use>...</tool_use>`, or no textual tool envelope at all because tool calls are injected by the runtime outside the assistant message content?

If possible, please provide one redacted successful raw assistant turn that dispatches `send_message_to_chat` in the live scaffold, including the outer formatting that the parser consumes, but excluding hidden reasoning or secrets.

## Retrain requirements after answer

1. Remove literal `<tool_use>...</tool_use>` XML from assistant targets unless admin confirms it is exactly scaffold-native.
2. Train positive chat actions in the parser-native output format only.
3. Train negative/no-chat rows without bracket sentinels that can leak into positives.
4. Add held-out tests for raw-envelope-in-memory/message loops, including `send_message_to_chat`, `pause`, and `get_pixel_coords_of_element` raw-envelope variants.
5. Treat v8 only as a gated diagnostic unless parser-format evidence says its target format is safe.
