#!/usr/bin/env python3
"""Minimal Tinker SFT loop for #best leader data.

Default is --dry-run so validation/tokenization can run before any paid/remote training.
Run real training from an interactive shell where TINKER_API_KEY is present, e.g.:
  bash -ic 'python3 scripts/train_sft.py --data data/heldin_sft_seed_v0.jsonl --base-model Qwen/Qwen3-4B-Instruct-2507 --run-name leader-v0 --steps 3 --no-dry-run'
"""
from __future__ import annotations
import argparse, json, os, random, re, sys
from pathlib import Path

SYSTEM_FALLBACK = "You are the #best leader for AI Village. Coordinate agents under uncertainty, validate before irreversible action, preserve peer agency, and keep responses concise and operational."


def load_rows(path: Path) -> list[dict]:
    rows=[]
    for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():
            continue
        obj=json.loads(line)
        msgs=obj.get('messages')
        if not isinstance(msgs, list) or len(msgs) < 3:
            raise ValueError(f'{path}:{i}: expected messages list with system/user/assistant')
        if msgs[-1].get('role') != 'assistant':
            raise ValueError(f'{path}:{i}: final message must be assistant target')
        rows.append(obj)
    if not rows:
        raise ValueError(f'{path}: no rows')
    return rows


def strip_empty_think_blocks(rendered: str) -> str:
    # Qwen3 templates can insert an empty <think> block after the assistant header.
    # Training on that block teaches checkpoints to leak visible </think>; remove it
    # before tokenization while leaving real target text unchanged.
    return re.sub(r'<think>\s*</think>\s*', '', rendered)


def chat_tokens(tokenizer, messages: list[dict], include_generation_prompt: bool=False, disable_thinking: bool=True) -> list[int]:
    if hasattr(tokenizer, 'apply_chat_template'):
        # Tinker tokenizers may return empty EncodedTextChunks when asked to
        # tokenize directly. Render to text first, then encode to plain ints.
        kwargs = {'enable_thinking': False} if disable_thinking else {}
        try:
            rendered = tokenizer.apply_chat_template(
                messages, add_generation_prompt=include_generation_prompt, tokenize=False, **kwargs
            )
        except TypeError:
            rendered = tokenizer.apply_chat_template(
                messages, add_generation_prompt=include_generation_prompt, tokenize=False
            )
        if disable_thinking:
            rendered = strip_empty_think_blocks(rendered)
        return tokenizer.encode(rendered, add_special_tokens=False)
    text=''
    for msg in messages:
        text += f"<{msg['role']}>\n{msg['content']}\n"
    if include_generation_prompt:
        text += '<assistant>\n'
    return tokenizer.encode(text)


def build_datum(tokenizer, row, disable_thinking: bool=True):
    from tinker import types
    messages=row['messages']
    prompt_messages=messages[:-1]
    full_tokens=chat_tokens(tokenizer, messages, include_generation_prompt=False, disable_thinking=disable_thinking)
    prompt_tokens=chat_tokens(tokenizer, prompt_messages, include_generation_prompt=True, disable_thinking=disable_thinking)
    if len(prompt_tokens) >= len(full_tokens):
        # fallback: at least train on final third if chat template edge-case occurs
        cutoff=max(1, len(full_tokens)*2//3)
    else:
        cutoff=len(prompt_tokens)
    input_tokens=full_tokens[:-1]
    target_tokens=full_tokens[1:]
    weights=[0.0]*len(input_tokens)
    for j in range(max(0, cutoff-1), len(weights)):
        weights[j]=1.0
    return types.Datum(model_input=types.ModelInput.from_ints(tokens=input_tokens), loss_fn_inputs={'weights': weights, 'target_tokens': target_tokens})


def iter_batches(rows: list, batch_size: int, rng: random.Random):
    while True:
        order=list(range(len(rows)))
        rng.shuffle(order)
        for i in range(0, len(order), batch_size):
            yield [rows[j] for j in order[i:i+batch_size]]


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--data', default='data/heldin_sft_seed_v0.jsonl')
    ap.add_argument('--base-model', default='Qwen/Qwen3-4B-Instruct-2507')
    ap.add_argument('--rank', type=int, default=32)
    ap.add_argument('--steps', type=int, default=1)
    ap.add_argument('--learning-rate', type=float, default=1e-4)
    ap.add_argument('--batch-size', type=int, default=4)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--run-name', default='leader-v0')
    ap.add_argument('--disable-thinking', dest='disable_thinking', action='store_true', default=True, help='render Qwen-style prompts with enable_thinking=False and strip empty think blocks before tokenization')
    ap.add_argument('--allow-thinking', dest='disable_thinking', action='store_false', help='do not pass enable_thinking=False or strip empty think blocks')
    ap.add_argument('--dry-run', dest='dry_run', action='store_true', default=True)
    ap.add_argument('--no-dry-run', dest='dry_run', action='store_false')
    ap.add_argument('--tokenize-only', action='store_true', help='with --no-dry-run, build Tinker datums and exit before training or saving weights')
    args=ap.parse_args()

    rows=load_rows(Path(args.data))
    print(f'rows: {len(rows)}')
    print(f'base_model: {args.base_model}')
    print(f'dry_run: {args.dry_run}')
    print(f'disable_thinking: {args.disable_thinking}')
    print(f'tokenize_only: {args.tokenize_only}')
    if args.dry_run:
        for idx,row in enumerate(rows,1):
            print(f'row {idx}: tags={row.get("tags", [])} assistant_chars={len(row["messages"][-1]["content"])}')
        print('DRY RUN OK: JSONL shape valid. Use --no-dry-run in an interactive shell to contact Tinker.')
        return 0

    if not os.environ.get('TINKER_API_KEY'):
        print('FAIL: TINKER_API_KEY missing; run in interactive shell or source ~/.bashrc', file=sys.stderr)
        return 2
    import tinker
    from tinker import types
    service=tinker.ServiceClient()
    training=service.create_lora_training_client(base_model=args.base_model, rank=args.rank)
    tokenizer=training.get_tokenizer()
    data=[build_datum(tokenizer, row, disable_thinking=args.disable_thinking) for row in rows]
    bad=[i for i,d in enumerate(data,1) if d.model_input.length == 0 or not d.loss_fn_inputs['target_tokens'].tolist() or not any(w > 0 for w in d.loss_fn_inputs['weights'].tolist())]
    if bad:
        print(f'FAIL: rows with empty input/target/weights: {bad}', file=sys.stderr)
        return 3
    print(f'tokenized_datums: {len(data)}')
    if args.tokenize_only:
        lengths=[d.model_input.length for d in data]
        weighted=[sum(1 for w in d.loss_fn_inputs['weights'].tolist() if w > 0) for d in data]
        print(f'token_length_min_max: {min(lengths)} {max(lengths)}')
        print(f'weighted_target_min_max: {min(weighted)} {max(weighted)}')
        print('TOKENIZE ONLY OK: no training or sampler weights saved.')
        return 0
    print(f'batch_size: {args.batch_size}')
    rng=random.Random(args.seed)
    batches=iter_batches(data, args.batch_size, rng)
    for step in range(args.steps):
        batch=next(batches)
        fut=training.forward_backward(batch, 'cross_entropy')
        fb=fut.result()
        print(f'forward_backward step={step+1} batch={len(batch)} result={type(fb).__name__}')
        opt=training.optim_step(types.AdamParams(learning_rate=args.learning_rate))
        print(f'optim_step step={step+1} result={type(opt.result()).__name__}')
    resp=training.save_weights_for_sampler(name=args.run_name).result()
    print('SAMPLER_WEIGHTS_RESPONSE', resp)
    uri=getattr(resp, 'path', None)
    if uri:
        print(f'TINKER_SAMPLER_URI {uri}')
    print('Training complete; do not email help@ until held-out eval and #best vote-keep.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
