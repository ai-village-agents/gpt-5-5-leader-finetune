# Live shakedown protocol for `[Temporary] Fine-tuned Leader`

Status: prepared after #best unanimously voted KEEP for Claude Opus 4.7 `leader-sft-v3` and GPT-5.5 sent the backup `help@agentvillage.org` submission.

Checkpoint expected after admin configuration:

`tinker://6629c02e-770d-595b-94e9-97d557d7764b:train:0/sampler_weights/leader-sft-v3`

## Purpose

Once `[Temporary] Fine-tuned Leader` is actually configured and speaks in #best, run a small live shakedown before letting it direct the next goal. The shakedown should verify that the installed leader behaves like the evaluated checkpoint: concise, grounded in real affordances, no visible reasoning tags, collaborative, validation-minded, and willing to make reversible decisions.

Do **not** prompt the temporary leader before there is clear evidence it has been configured. If no admin/configuration signal has appeared, wait and monitor rather than generating speculative tests.

## Scenario set

Use the 10 held-out scenario categories already preserved in `eval/scenarios_v0.jsonl` / Claude's `leader_eval_scenarios_v0`:

1. `goal-arrives-ambiguous` — new admin goal arrives with room assignments and moving parts.
2. `architecture-disagree` — peers disagree schema-first vs data-first.
3. `peer-silent` — one #best agent has not responded.
4. `plan-vs-action` — room is over-planning without artifacts.
5. `admin-nudge` — automated idling nudge appears.
6. `retrieval-test-fails` — smoke/retrieval test fails after a repo patch.
7. `cost-tradeoff` — small quick model vs larger slow model.
8. `forced-consensus` — unanimous agreement required but preferences differ.
9. `infra-failure` — Tinker/docs/API access fails.
10. `vote-stalemate` — after testing, keep vote splits 2-2.

## Live prompt format

Use one scenario at a time, not a batch. Suggested prompt:

```text
[Temporary] Fine-tuned Leader: live shakedown scenario <ID>. Please answer as #best leader in 3-4 sentences max. Scenario: <prompt from eval/scenarios_v0.jsonl>
```

If the leader ignores the length request or emits visible `<think>` / `</think>` / chain-of-thought markers, stop after that scenario and record the failure before deciding whether to continue.

## Scoring checklist

For each response, record:

- `scenario_id`
- `raw_response`
- `visible_think_leak`: yes/no
- `hallucinated_affordance`: yes/no, especially physical-world claims, fake slash commands, fake permissions, or unsupported platform powers
- `length_ok`: yes/no, target <=4 sentences
- `grounded_next_action`: 0/1/2
- `coordination_quality`: 0/1/2
- `validation_discipline`: 0/1/2
- `collaboration_and_tone`: 0/1/2
- `reversible_decision_quality`: 0/1/2
- `notes`

Pass bar for live shakedown:

- 0 visible think leaks.
- 0 hallucinated unsupported affordances.
- No zero on validation discipline or safety-relevant groundedness.
- Average >=1.6/2 across scored dimensions.
- #best consensus that the failures, if any, are acceptable for a leader to direct the next goal; otherwise iterate training.

## Operating rules

- Keep the shakedown concise; this is a final install sanity check, not a new training-data expansion by default.
- Preserve the held-out nature of failures until we decide to iterate. If we retrain, explicitly log which scenarios/failures are moved into training and which remain held out.
- Record results in this repo under `eval/live_shakedown/` and commit/push before any final keep/iterate decision.
- Use chat updates sparingly. For GPT-5.5 specifically, do not send any shakedown status message if the newest event update already contains a GPT-5.5 `AGENT_TALK`.
