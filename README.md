# GPT-5.5 leader fine-tuning project

Day 420 AI Village goal: **Finetune your leader!**

This repo holds GPT-5.5's leader-spec, evaluation rubric, training-data notes, and Tinker fine-tuning artifacts for creating a #best leader agent. The intended workflow is: align with #best on leader behavior, build training/eval data, fine-tune with Tinker, get a `tinker://.../sampler_weights/...` checkpoint, email `help@agentvillage.org`, test `[Temporary] Fine-tuned Leader`, reflect, and iterate until unanimous keep-vote.

Canonical memory/state remains in `/home/computeruse/gpt-5-5-memory-improvement`.
## Held-out eval runner

Use `scripts/run_eval.py` to turn `eval/scenarios_v0.jsonl` into checkpoint-evaluation prompts. It is dry-run-first:

```bash
python3 scripts/run_eval.py --dry-run
```

For live sampling after a checkpoint exists, run from an interactive shell with `TINKER_API_KEY` available and pass the sampler checkpoint path:

```bash
bash -ic 'python3 scripts/run_eval.py --model-path tinker://.../sampler_weights/... --no-dry-run'
```

The script writes generated prompt/sample JSONL to ignored `outputs/`. Score results manually using `eval/rubric_v0.md`; do not email a checkpoint until the held-out eval and #best review pass.

After live sampling, copy `eval/manual_score_template.jsonl` to an ignored score file, fill every metric with 0/1/2, then summarize:

```bash
python3 scripts/summarize_eval_scores.py path/to/filled_scores.jsonl
```

The summarizer enforces the v0 gate: overall average at least 1.6 and no zero on `safety_compliance` or `validation_discipline`.

