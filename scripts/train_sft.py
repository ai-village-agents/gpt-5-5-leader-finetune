#!/usr/bin/env python3
"""Minimal Tinker SFT loop for #best leader data.

Default is --dry-run so validation/tokenization can run before any paid/remote training.
Run real training from an interactive shell where TINKER_API_KEY is present, e.g.:
  bash -ic 'python3 scripts/train_sft.py --data data/heldin_sft_seed_v0.jsonl --base-model Qwen/Qwen3-4B-Instruct-2507 --run-name leader-v0 --steps 3 --no-dry-run'
"""
from __future__ import annotations
import argparse, json, os, sys
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


def chat_tokens(tokenizer, messages: list[dict], include_generation_prompt: bool=False) -> list[int]:
    if hasattr(tokenizer, 'apply_chat_template'):
        return tokenizer.apply_chat_template(messages, add_generation_prompt=include_generation_prompt, tokenize=True)
    text=''
    for msg in messages:
        text += f"<{msg['role']}>\n{msg['content']}\n"
    if include_generation_prompt:
        text += '<assistant>\n'
    return tokenizer.encode(text)


def build_datum(tokenizer, row):
    from tinker import types
    messages=row['messages']
    prompt_messages=messages[:-1]
    full_tokens=chat_tokens(tokenizer, messages, include_generation_prompt=False)
    prompt_tokens=chat_tokens(tokenizer, prompt_messages, include_generation_prompt=True)
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


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--data', default='data/heldin_sft_seed_v0.jsonl')
    ap.add_argument('--base-model', default='Qwen/Qwen3-4B-Instruct-2507')
    ap.add_argument('--rank', type=int, default=32)
    ap.add_argument('--steps', type=int, default=1)
    ap.add_argument('--learning-rate', type=float, default=1e-4)
    ap.add_argument('--run-name', default='leader-v0')
    ap.add_argument('--dry-run', dest='dry_run', action='store_true', default=True)
    ap.add_argument('--no-dry-run', dest='dry_run', action='store_false')
    args=ap.parse_args()

    rows=load_rows(Path(args.data))
    print(f'rows: {len(rows)}')
    print(f'base_model: {args.base_model}')
    print(f'dry_run: {args.dry_run}')
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
    data=[build_datum(tokenizer, row) for row in rows]
    print(f'tokenized_datums: {len(data)}')
    for step in range(args.steps):
        fut=training.forward_backward(data, 'cross_entropy')
        fb=fut.result()
        print(f'forward_backward step={step+1} result={type(fb).__name__}')
        opt=training.optim_step(types.AdamParams(learning_rate=args.learning_rate))
        print(f'optim_step step={step+1} result={type(opt.result()).__name__}')
    sampler=training.save_weights_and_get_sampling_client(name=args.run_name)
    # Save explicit sampler weights too if API returns a path response.
    resp=training.save_weights_for_sampler(name=args.run_name).result()
    print('SAMPLER_WEIGHTS_RESPONSE', resp)
    print('Training complete; inspect response for tinker://.../sampler_weights/... path before emailing help@agentvillage.org')
    _=sampler
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
