#!/usr/bin/env python3
"""Export/sample scaffolding-shaped eval prompts for v4 leader checkpoints."""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
from typing import Any


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    rows=[]
    for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        obj=json.loads(line)
        for k in ('id','expected_action','must_include','must_not_include','prompt','scoring_notes'):
            if k not in obj: raise ValueError(f'{path}:{i}: missing {k}')
        rows.append(obj)
    if not rows: raise ValueError(f'{path}: no scenarios')
    return rows


def chat_tokens(tokenizer, messages, disable_thinking=True):
    if hasattr(tokenizer, 'apply_chat_template'):
        kwargs={'enable_thinking': False} if disable_thinking else {}
        rendered=tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False, **kwargs)
        encoded=tokenizer.encode(rendered, add_special_tokens=False)
    else:
        rendered=''.join(f"<{m['role']}>\n{m['content']}\n" for m in messages) + '<assistant>\n'
        encoded=tokenizer.encode(rendered)
    if isinstance(encoded, dict): encoded=encoded.get('input_ids', encoded)
    if hasattr(encoded, 'input_ids'): encoded=encoded.input_ids
    return list(encoded)


def response_samples(resp):
    for attr in ('samples','outputs','responses','sequences'):
        if hasattr(resp, attr):
            val=getattr(resp, attr)
            if isinstance(val,(list,tuple)): return list(val)
    return resp if isinstance(resp, list) else [resp]


def sample_to_text(sample, tokenizer):
    if isinstance(sample, str): return sample
    for attr in ('text','content','completion'):
        if hasattr(sample, attr) and isinstance(getattr(sample, attr), str): return getattr(sample, attr)
    for attr in ('tokens','token_ids','output_tokens'):
        if hasattr(sample, attr):
            toks=getattr(sample, attr)
            if isinstance(toks, list):
                try: return tokenizer.decode(toks, skip_special_tokens=True)
                except Exception: return str(toks)
    return repr(sample)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--scenarios', default='eval/scaffolding_v4/scenarios_v0.jsonl')
    ap.add_argument('--output-dir', default='outputs')
    ap.add_argument('--base-model', default='Qwen/Qwen3-8B')
    ap.add_argument('--model-path', default=None)
    ap.add_argument('--max-tokens', type=int, default=260)
    ap.add_argument('--temperature', type=float, default=0.2)
    ap.add_argument('--top-p', type=float, default=0.95)
    ap.add_argument('--seed', type=int, default=420)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--disable-thinking', dest='disable_thinking', action='store_true', default=True)
    ap.add_argument('--allow-thinking', dest='disable_thinking', action='store_false')
    ap.add_argument('--dry-run', dest='dry_run', action='store_true', default=True)
    ap.add_argument('--no-dry-run', dest='dry_run', action='store_false')
    args=ap.parse_args()
    scenarios=load_scenarios(Path(args.scenarios))
    if args.limit: scenarios=scenarios[:args.limit]
    out_dir=Path(args.output_dir); out_dir.mkdir(parents=True, exist_ok=True)
    stamp=time.strftime('%Y%m%d-%H%M%S')
    out_path=out_dir / (f'scaffolding_eval_prompts_{stamp}.jsonl' if args.dry_run else f'scaffolding_eval_samples_{stamp}.jsonl')
    print(f'scaffolding_scenarios: {len(scenarios)}')
    print(f'dry_run: {args.dry_run}')
    print(f'output: {out_path}')
    if args.dry_run:
        with out_path.open('w', encoding='utf-8') as f:
            for s in scenarios:
                f.write(json.dumps({k:s[k] for k in ('id','expected_action','must_include','must_not_include','prompt','scoring_notes')}, ensure_ascii=False)+'\n')
        print('DRY RUN OK: wrote scaffolding eval prompts only; no Tinker call made.')
        return 0
    if not os.environ.get('TINKER_API_KEY'):
        raise SystemExit('FAIL: TINKER_API_KEY missing; run via bash -ic')
    import tinker
    from tinker import types
    service=tinker.ServiceClient()
    sampler=service.create_sampling_client(model_path=args.model_path) if args.model_path else service.create_sampling_client(base_model=args.base_model)
    tokenizer=sampler.get_tokenizer()
    params=types.SamplingParams(max_tokens=args.max_tokens, temperature=args.temperature, top_p=args.top_p, seed=args.seed)
    with out_path.open('w', encoding='utf-8') as f:
        for s in scenarios:
            msgs=s['prompt']['messages']
            prompt=types.ModelInput.from_ints(tokens=chat_tokens(tokenizer, msgs, disable_thinking=args.disable_thinking))
            resp=sampler.sample(prompt, num_samples=1, sampling_params=params).result()
            samples=response_samples(resp)
            text=sample_to_text(samples[0], tokenizer) if samples else repr(resp)
            rec={**{k:s[k] for k in ('id','expected_action','must_include','must_not_include','prompt','scoring_notes')}, 'response': text, 'model_path': args.model_path, 'base_model': None if args.model_path else args.base_model}
            f.write(json.dumps(rec, ensure_ascii=False)+'\n'); f.flush()
            print(f"sampled {s['id']}: {len(text)} chars")
    print(f'SCAFFOLDING EVAL SAMPLES WRITTEN: {out_path}')
    return 0

if __name__=='__main__': main()
