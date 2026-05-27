# GPT-5.5 v12 Claude-tool-contract hard positives

Four hard-positive rows targeting the exact Claude-tool-contract prompt-shape cases that Claude v11 over-gated in GPT-5.5 independent eval.

Rows: fresh empty memory, addressed shakedown scenario, admin-stopped-leader, and peer-disagreement/base-vs-shape under `--claude-system`.

Assistant targets are exact `<tool_use>` / `send_message_to_chat` envelopes and contain no bracketed no-chat sentinel strings. Intended use: rebalance v12 so tool-contract prompts are not dominated by clean no-chat negatives.
