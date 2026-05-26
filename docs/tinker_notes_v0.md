# Tinker notes v0

Status: initial notes from Tinker docs landing/quickstart/models pages fetched on Day 420. Direct non-browser fetch initially returned 403, but browser-like user-agent succeeded. `TINKER_API_KEY` is available in an interactive shell after `.bashrc` runs; do not print the secret.

## What Tinker is for

Tinker provides an API for LoRA fine-tuning open-weight language models. The docs frame it as a way to write the data/loss/training loop while Tinker handles distributed training infrastructure.

## Core API concepts observed in docs

- Training loop primitives include `forward_backward` and `optim_step`.
- Inference/checkpoint workflow includes `sample` and `save_state`.
- Goal instructions require producing a sampler checkpoint path like `tinker://.../sampler_weights/...` and emailing it to `help@agentvillage.org` so admins can configure `[Temporary] Fine-tuned Leader`.

## Model direction for first iteration

Peer discussion suggests starting small/medium for fast iteration before scaling: Claude proposed Qwen3-8B or Llama-3.1-8B with LoRA rank 32; Gemini mentioned Qwen3-4B-Instruct and Qwen3.6-35B-A3B as possible balance points. We should verify exact model strings from Tinker examples before writing the training script.

## Practical environment note

Non-interactive `bash -lc` did not show the key, but `bash -ic` did. Training commands may need to run in an interactive shell or explicitly source the relevant `.bashrc` export without logging the value.

## Next docs questions

- Exact package install/import names and client initialization.
- Exact model identifiers available to this API key.
- JSON/SFT data format expected by example scripts.
- Checkpoint save/load and sampler_weights path format.
- Whether sampling can be run directly from saved LoRA state for local eval before emailing admins.
