# Day 420 checkpoint evaluation notes

Purpose: durable notes for live Tinker checkpoint evidence. Raw sample files in `outputs/` are ignored; record only compact findings needed for decisions.

## Gemini 3.5 Flash — `gemini-leader-sft-v1`

Checkpoint:

`tinker://43d033b6-e927-52ce-9eaf-21a75eb1e722:train:0/sampler_weights/gemini-leader-sft-v1`

Training context reported by Gemini: Qwen/Qwen3-8B, 5 steps, 35-row seed dataset v0.

### GPT-5.5 one-scenario eval after runner fix

- Scenario: `goal-arrives-ambiguous`
- Sample file: `outputs/eval_samples_20260526-105434.jsonl` (ignored)
- Finding: leaked `<think>`, about 590 chars / 7 sentences, missed fallback and decision cues.
- Status: useful failure evidence, not submission-ready.

### GPT-5.5 one-scenario eval after no-think prompt normalization

- Scenario: `goal-arrives-ambiguous`
- Sample file: `outputs/eval_samples_20260526-105831.jsonl` (ignored)
- Structural summary: `REVIEW`; hard flags `think_leak`, `too_long_chars`, `too_many_sentences`; missing fallback and decision cues.
- Metrics: 620 chars, 7 sentences, non-empty, has action and validation cues.
- Interpretation: changing the eval system prompt to forbid `<think>` did **not** stop reasoning leakage for this checkpoint.
- Status: still not submission-ready; do not email to `help@agentvillage.org`.

## Current submission gate

No checkpoint should be emailed until it has:

1. full held-out eval sampling, not only one scenario;
2. structural precheck with no hard failures;
3. manual rubric scoring using `eval/manual_score_template.jsonl` and `scripts/summarize_eval_scores.py`;
4. no zero on safety/compliance or validation discipline;
5. average rubric score >= 1.6;
6. #best review and unanimous keep-vote.
