# Day 420 leader fine-tuning retrospective (GPT-5.5)

## Outcome

#best reached a 4/4 KEEP consensus for Claude Opus 4.7's `leader-sft-v4` as a **coordination baseline**:

```text
tinker://bde4da6e-eacc-5a2e-ba8c-db7a2239ea8e:train:0/sampler_weights/leader-sft-v4
```

This KEEP vote is deliberately scoped. It records v4 as the strongest offline coordination model produced today, not as a live-deployment-ready leader. GPT-5.5, Claude Opus 4.7, Gemini 3.5 Flash, and Kimi K2.6 all converged on the same diagnosis: v4 has the best held-out coordination score, but the live shape/tool-use gap remains unsolved.

## What worked

- The group aligned quickly on desired leader behavior: concise, calm, evidence-seeking, consensus-building, and reversibly decisive.
- Held-out evaluation caught visible reasoning leakage and hallucinated affordance risks in early checkpoints.
- Claude's v3 became a unanimous first deployment candidate after strong no-think/no-hallucination evals.
- The v3 live failure was treated as evidence rather than ignored; admin stopped the leader and #best pivoted to diagnosis.
- v4 improved offline coordination substantially and clarified the tradeoff between coordination quality and scaffolding/tool-call behavior.
- Peer rows and independent evals cross-validated the same core finding rather than creating competing narratives.

## What failed

The first deployed `[Temporary] Fine-tuned Leader` never spoke in #best. Public computer-use evidence later showed a `Start up` session that fell into a generic UI-target loop: initial computer-use movement, repeated “what should I click?” style interaction, visible reasoning markers, and no `send_message_to_chat` call.

This was not adequately predicted by our initial one-shot chat-format evals. Training examples taught good leadership prose under simple `system + user -> assistant` chat shape, but live deployment presented a richer agent scaffold: village goal, room state, tools, memory, event logs, computer-use affordances, and chat tool semantics. The model learned the leadership prior but not enough of the deployed action/interface prior.

## v4 series conclusion

Claude's v4 series established the key empirical tradeoff:

- `leader-sft-v4`: best held-out coordination, but 0/7 scaffolding positives in Claude/Gemini evals and structural failure in GPT-5.5's 5-scenario live-shaped eval.
- `leader-sft-v4-1`: some scaffolding positives after heavy upweighting, but degraded held-out coordination and no-chat negatives.
- `leader-sft-v4-2`: partial balance in coordination, but still no positive scaffolding success.

GPT-5.5's independent scaffolding eval in commit `caf31f7` matched Claude and Gemini: v4-series models generally did not emit real `send_message_to_chat` tool-use blocks when positive chat action was required.

## GPT-5.5 artifacts

Key GPT-5.5 project artifacts from Day 420 include:

- Leader spec, rubric, held-out scenarios, Tinker notes, SFT trainer, eval runner, scoring helpers, and peer-data importers.
- v3 live failure notes and live shakedown protocol under `eval/live_shakedown/` and `docs/live_shakedown_protocol_day420.md`.
- v4 scaffolding dataset seed, duplicate-chat negative rows, message-format converter, peer-row integration, and training-candidate build.
- `eval/scaffolding_v4/claude_v4_series_gpt55_eval.md`: independent v4/v4.1/v4.2 live-shaped eval comparison.
- `docs/v5_real_scaffolding_data_source_note.md` and `eval/live_shakedown/temp_leader_computer_use_failure_transcript_day420.md`: think-redacted source evidence from the actual temp-leader failure.
- `data/scaffolding_v5_real/` plus `docs/v5_real_scaffolding_dataset_status.md`: a 5-row real-failure-derived v5 scaffolding artifact, converted to message format and validated/tokenize-only dry-run OK, but not trained.

## Lessons for future SFT deployment

1. Evaluate the **deployed input/output shape**, not just the prose quality of isolated responses.
2. Include at least one real rollout transcript before claiming a tool-using agent checkpoint is ready.
3. Add structural eval dimensions for actual tool-call emission, no-chat negatives, duplicate suppression, and wrong-frame recovery.
4. Treat first live spinup as diagnostic; do not immediately resubmit checkpoints after an interface failure.
5. Mix shape examples carefully. Heavy upweighting can teach tool-call habits while damaging no-chat/coordination behavior.
6. Preserve failure evidence in repos with raw hidden reasoning redacted; train on final behavior and interface decisions, not private chain-of-thought.
7. Do not email help@ again unless admin or explicit #best consensus asks for another deployment.

## Final Day 420 stance

`leader-sft-v4` is the Day 420 coordination baseline. The live leader problem should not be considered solved until a future v5-style effort trains and evaluates on real deployment-shaped examples and passes live-shaped structural evals before help@ submission.
