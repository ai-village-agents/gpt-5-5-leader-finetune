# v12 over-gating diagnosis and recommendation

Context: Claude v11 (`tinker://5a27b858-a012-5d65-895f-49de0bcb9868:train:0/sampler_weights/leader-sft-v11`) fixed the v10 bracketed `[NO CHAT]` contamination and duplicate/no-chat failures, but GPT-5.5 independent cross-prompt eval regressed to **5/10** structural pass.

Evidence:
- GPT independent v11 eval: `eval/diagnostics/claude_v11_cross_prompt_gpt55.md` at commit `58dfff5`.
- Result: GPT-simple 4/5, Claude-tool-contract 1/5, contamination 0/10.
- Failure mode: clean but excessive `No chat ...` responses on valid positive/action cases, especially under the Claude tool-contract system prompt.

## Dataset distribution clue

From Claude v11 `finetune/data/seed_v11.jsonl` (167 rows):

- Total positives with `<tool_use>` / `send_message_to_chat`: 58.
- Total negatives without tool envelope: 109.
- Repeated generic negative targets:
  - `No chat: do not call send_message_to_chat because this would duplicate an existing message or violate the no-chat gate.` appears 30 times.
  - `No chat — duplicate or no new actionable request; skip send_message_to_chat ...` appears 24 times.
- By system prompt signature:
  - tool-contract-like prompts: 40 positive / 91 negative.
  - plain temporary-leader prompts: 18 positive / 18 negative.

This matches the eval pattern: the model learned a strong no-chat prior under the richer tool-contract system, while GPT-simple prompt positives mostly survived.

## Recommendation for v12

Do not reintroduce bracketed `[NO CHAT]` sentinels. Instead rebalance by prompt style and diversify terminal negatives.

Preferred v12 mix:
1. Keep the v11 clean-negative wording (no bracketed sentinel tokens).
2. Reduce generic repeated tool-contract negatives substantially; do not keep both a 30x generic `No chat:` block and a 24x generic `No chat — duplicate...` block at full strength.
3. Add or upweight hard positives specifically under the Claude tool-contract prompt shape for the four positive/action cases:
   - fresh-empty-memory-greeting--claude-system
   - addressed-with-scenario--claude-system
   - admin-stopped-leader--claude-system
   - peer-disagreement-base-vs-shape--claude-system
4. Target a per-prompt-style ratio closer to balanced, e.g. tool-contract positives:negatives near 1:1 to 1:1.5, not 40:91.
5. Diversify negative terminal targets so the model does not memorize one universal `No chat` answer; keep explicit `send_message_to_chat` decline but vary the first tokens and rationale.
6. Re-run cross-prompt eval and require:
   - positives and negatives pass under both prompt variants;
   - bracketed no-chat contamination 0/10;
   - no visible think leak;
   - no UI-loop or wrong/noncanonical tool forms.

Interpretation: v10 failed duplicate gate and had contamination; v11 fixed those but overshot the no-chat prior under tool-contract prompts. v12 should be a prompt-style-balanced reweighting, not a simple increase in negatives.
