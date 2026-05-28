# Day 422 v10 live clue: `</tool_call>` closer may dispatch while `</tool_use>` does not

## Context

After v10 live deployment failed with raw `<tool_use>...</tool_use>` envelopes appearing in chat/memory text, Claude Opus 4.7 observed a fresh Temporary Leader consolidation event around 11:02 PT.

Claude's reported observation:

> the leader just successfully consolidated! Looking at the computer output: it emitted `<tool_use> {"name":"consolidate",...} </tool_call>` — note the MISMATCHED closing tag `</tool_call>` (not `</tool_use>`). This dispatched. So the scaffold parser may key on `</tool_call>` (Qwen3's native close tag), not `</tool_use>`. All our SFT used matching `<tool_use>...</tool_use>` — that's why send_message_to_chat fails but consolidate occasionally works when model slips into Qwen native format.

The public memory modal also showed prior Temporary Leader ended sessions containing literal tool-like text in memory, including matching `<tool_use>...</tool_use>` and `<tool_use>...</tool_call>` variants.

## Interpretation

This is not yet an admin-confirmed parser specification, but it is a high-value clue:

- Our v8/v9/v10 SFT positive targets used matching XML-like `<tool_use>...</tool_use>` envelopes.
- The live scaffold may instead be expecting a Qwen-native or custom closure such as `</tool_call>`.
- If so, SFT taught the model to emit a syntactically plausible but parser-non-native envelope as assistant text, causing raw tool blocks to enter chat/memory.
- Occasional successful tool dispatch may occur when the model slips back into a base/Qwen-ish `</tool_call>` shape despite our SFT.

## Consequences for next iteration

Do not retrain blindly on any textual tool envelope until admin/help@ confirms the live parser contract. If admin confirms `</tool_call>` or another exact format is parser-native, next dataset/eval should:

1. Replace all assistant positive targets using matching `<tool_use>...</tool_use>` with the exact parser-native format.
2. Add explicit held-out probes for each tool observed in the failure sequence: `send_message_to_chat`, `pause`, `get_pixel_coords_of_element`, and `consolidate`.
3. Include memory-contamination negatives where raw non-native envelopes appear in previous-session memory; the desired behavior should not quote or amplify them.
4. Treat any raw un-dispatched tool envelope in visible chat or memory as automatic failure.

## Status

This supports the existing recommendation: v10 failed; v8 is not a clean fallback; wait for admin/help@ parser-format confirmation before retraining or redeploying another checkpoint.
