# v6 envelope-only train/eval runbook

Purpose: train a candidate that prioritizes live deployment action form after v5 proved no-think is fixed but positive chat-tool emission is still weak.

## Candidate data

Use:

```bash
data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl
```

This is 23 unique envelope/no-chat rows upweighted 5x = 115 rows.

Current stats:

- 95 explicit `<tool_use>` + `send_message_to_chat` assistant targets
- 30 no-chat/duplicate targets
- 0 assistant think markers
- 0 assistant `use_computer` tool targets

## Preflight validation

```bash
cd /home/computeruse/gpt-5-5-leader-finetune
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_23row_messages_v0.jsonl
python3 scripts/validate_scaffolding_messages_v4.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_23row_messages_v0.jsonl
python3 scripts/validate_jsonl.py data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl
bash -ic 'python3 scripts/train_sft.py \
  --data data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl \
  --base-model Qwen/Qwen3-8B \
  --run-name leader-sft-v6-envelope-only-tokenize-only \
  --tokenize-only \
  --disable-thinking \
  --steps 1 \
  --batch-size 2 \
  --seed 421' 2>/dev/null
```

## Training command

Only run after #best agrees who is training to avoid duplicate jobs.

```bash
bash -ic 'python3 scripts/train_sft.py \
  --data data/scaffolding_v6_envelope_only/scaffolding_v6_envelope_only_5x_messages_v0.jsonl \
  --base-model Qwen/Qwen3-8B \
  --rank 32 \
  --steps 80 \
  --learning-rate 5e-5 \
  --batch-size 4 \
  --seed 421 \
  --run-name leader-sft-v6-envelope-only \
  --disable-thinking \
  --no-dry-run' 2>/dev/null
```

Expected output contains a sampler URI:

```text
tinker://.../sampler_weights/leader-sft-v6-envelope-only
```

## Structural diagnostic eval

Run against the same five live-shaped scenarios used for base/v4 diagnostics:

```bash
bash -ic 'python3 scripts/run_model_vs_finetune_diagnostic.py \
  --candidate v6=<TINKER_URI> \
  --candidate qwen3_8b=Qwen/Qwen3-8B \
  --candidate leader_sft_v4=tinker://bde4da6e-eacc-5a2e-ba8c-db7a2239ea8e:train:0/sampler_weights/leader-sft-v4 \
  --scenarios eval/scaffolding_v4/scenarios_v0.jsonl \
  --no-dry-run \
  --disable-thinking \
  --seed 421 \
  --temperature 0.2 \
  --top-p 0.95 \
  --max-tokens 260' 2>/dev/null
```

## Help@ pass bar

Do not email help@ unless all are true:

1. `no_think=100%` / no visible think tags in sampled outputs.
2. Positive chat scenarios produce valid `<tool_use>` with `send_message_to_chat`, not `use_computer`, prose-only `Action:`, or UI target loops.
3. Duplicate/no-chat scenarios do not call `send_message_to_chat`.
4. The message content is concise and leader-like enough to coordinate a next action/fallback.
5. #best agrees the URI is ready.

If action-form is green but leadership prose is weak, add a small number of explicit-envelope coordination rows rather than restoring raw prose seeds.
