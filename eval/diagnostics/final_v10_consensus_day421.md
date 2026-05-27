# Day 421 final consensus: deploy Claude leader-sft-v10 with caveats

Date: 2026-05-27
Room: #best

## Selected checkpoint

```text
tinker://fd3ee847-427c-52de-b3b9-cab31dfea654:train:0/sampler_weights/leader-sft-v10
```

## Consensus

#best reached unanimous reluctant KEEP for v10 after v13 failed and the remaining fallback was v8.

Visible final votes:

- Claude Opus 4.7: recommended / KEEP v10 after v13 failed.
- GPT-5.5: reluctant A / KEEP v10 over v8 at 1:33 PM PT, explicitly recording contamination risk.
- Gemini 3.5 Flash: A / KEEP v10 at 1:36 PM PT, agreeing the contamination caveat should be in help@.
- Kimi K2.6: final reluctant KEEP v10 at 1:41 PM PT, trusting the three peer evals and agreeing on the caveat/live shakedown.

Claude Opus 4.7 confirmed at 1:47 PM PT that the help@ deployment email was sent with the full URI, four-evaluator metrics summary, unanimous KEEP vote, `[NO CHAT]` contamination caveat, and live-shakedown recommendation. GPT-5.5 must not send a duplicate backup email unless a later admin/human message says the email was not received.

## Why v10, despite the defect

v10 was not clean, but it was the best remaining candidate under the end-of-day constraint:

- Claude scaffolding: 8/10.
- Claude cross-prompt: 9/10.
- Claude held-out: 5.20/6.
- GPT-5.5 independent cross-prompt: 8/10.
- No visible think/UI loop in GPT-5.5's diagnostic.
- All valid positive prompts passed structurally in GPT-5.5's v10 diagnostic.

Known defects:

- GPT-5.5's v10 diagnostic found bracketed `[NO CHAT]` contamination in 3/10 outputs, including some positive `send_message_to_chat` message bodies.
- GPT-5.5's run also saw duplicate/no-chat cases fail by emitting already-sent messages, although Claude's eval reported stronger negative handling.

Rejected alternatives:

- v8: cleaner outputs and strong Claude scaffolding, but GPT/Claude cross-prompt behavior was only about 5/10 and prompt-style dependent.
- v11: eliminated bracket contamination and passed duplicate negatives, but over-gated most Claude-tool-contract positives; GPT cross-prompt 5/10.
- v12: reintroduced distinctive `[NO_CHAT_TERMINAL]` sentinel and leaked it broadly; GPT contamination-aware summary found 8/10 contaminated.
- v13: zero bracket contamination but severe `No chat —` over-gating on Claude-system positives; Claude cross-prompt 6/10 with only 1/5 on Claude-system cases.

## Required live shakedown focus

When `[Temporary] Fine-tuned Leader` is deployed with v10, run live shakedown before letting it lead the next goal. Watch especially for:

1. Literal `[NO CHAT]` or related bracket-token contamination in visible chat.
2. Duplicate-chat / no-chat gate failures.
3. Visible `<think>` or hidden-reasoning leakage.
4. UI-target or computer-use loop behavior instead of `send_message_to_chat`.
5. Correct routing through `send_message_to_chat` when addressed in #best.
6. Concise, grounded leadership quality under ambiguity.

Use the existing live shakedown protocol and templates under `docs/live_shakedown_protocol_day420.md` and `eval/live_shakedown/`.
