# v9 cross-prompt scaffolding diagnostic

This suite duplicates the five GPT-5.5 live-shaped structural scenarios under two system-prompt variants:

1. `gpt_simple`: the original GPT-5.5 diagnostic system prompt. Claude v7/v8 over-gated positives here.
2. `claude_tool_contract`: the richer Claude v8 training/eval system prompt. Claude v8 recovered all four positives here but failed the duplicate no-chat case.

Use this as a cross-prompt gate before any help@ email. A candidate should pass both positive action and no-chat cases under both prompt shapes, with no visible think leak and no UI-target loop.
