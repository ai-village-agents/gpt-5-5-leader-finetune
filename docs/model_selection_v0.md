# Base model selection v0

Status: initial recommendation for #best discussion, not final.

## Capability check

`bash -ic 'python3 scripts/list_tinker_models.py'` succeeded on Day 420 with `models_count: 39`. The API key is present in interactive shells, and the Tinker SDK was installed with `python3 -m pip install --user tinker`.

## Candidate bases seen in capability list / peer discussion

- `Qwen/Qwen3-4B-Instruct-2507` — Gemini suggested this as a small/medium SFT start; likely fast enough for iteration.
- `Qwen/Qwen3-8B` — Tinker quickstart examples use this; Claude suggested Qwen3-8B with LoRA rank 32.
- `meta-llama/Llama-3.1-8B-Instruct` — Claude suggested Llama 3.1 8B as another fast baseline.
- `Qwen/Qwen3.6-35B-A3B` — Gemini noted this as a larger MoE option; likely later if dataset/eval shape is validated.
- `moonshotai/Kimi-K2.6` — available and poetic, but likely too large/slow for first dataset validation.

## Recommendation

Start with a small/medium instruct model for SFT v0, preferably `Qwen/Qwen3-4B-Instruct-2507` if examples confirm the exact string supports LoRA creation, otherwise `Qwen/Qwen3-8B` because the quickstart uses it. Use LoRA rank 32. Scale only after held-out leadership scenarios show the dataset shape is useful.

## Decision rule

Pick the smallest model that can express the target leader behavior well enough to expose data/rubric flaws. Do not spend the first iteration on a large model before validating data format, checkpoint flow, and evaluation criteria.
