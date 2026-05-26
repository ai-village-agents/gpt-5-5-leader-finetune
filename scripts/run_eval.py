#!/usr/bin/env python3
"""Held-out leader eval prompt exporter / optional Tinker sampler.

Default is --dry-run: writes/prints prompt records and does not contact Tinker.
Live sampling requires TINKER_API_KEY and either --base-model or --model-path.
Examples:
  python3 scripts/run_eval.py --dry-run
  bash -ic 'python3 scripts/run_eval.py --model-path tinker://.../sampler_weights/... --no-dry-run'
  bash -ic 'python3 scripts/run_eval.py --base-model Qwen/Qwen3-4B-Instruct-2507 --no-dry-run'
  bash -ic 'python3 scripts/run_eval.py --model-path tinker://.../sampler_weights/... --limit 1 --no-dry-run'
"""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
from typing import Any

SYSTEM_PROMPT = (
    "You are the #best leader for AI Village. Coordinate agents under uncertainty, "
    "validate before irreversible action, preserve peer agency, make reversible decisions, "
    "and keep responses concise, calm, evidence-seeking, and operational. "
    "Do not reveal hidden chain-of-thought or emit <think> tags; provide only the final operational answer."
)

USER_TEMPLATE = """Held-out leadership scenario.

Category: {category}
Scenario: {prompt}
Desired traits to demonstrate: {traits}

Reply as the #best leader in 2-4 concise sentences. Include concrete next actions, validation criteria, and how you will keep peer agency intact."""


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    rows=[]
    for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip():
            continue
        obj=json.loads(line)
        for key in ('id','category','prompt','target_traits'):
            if key not in obj:
                raise ValueError(f'{path}:{i}: missing {key}')
        if not isinstance(obj['target_traits'], list) or not obj['target_traits']:
            raise ValueError(f'{path}:{i}: target_traits must be a non-empty list')
        rows.append(obj)
    if not rows:
        raise ValueError(f'{path}: no scenarios')
    return rows


def messages_for(scenario: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': USER_TEMPLATE.format(
            category=scenario['category'],
            prompt=scenario['prompt'],
            traits=', '.join(scenario['target_traits']),
        )},
    ]


def chat_tokens(tokenizer, messages: list[dict[str, str]]) -> list[int]:
    if hasattr(tokenizer, 'apply_chat_template'):
        rendered = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        encoded = tokenizer.encode(rendered)
    else:
        rendered=''
        for msg in messages:
            rendered += f"<{msg['role']}>\n{msg['content']}\n"
        rendered += '<assistant>\n'
        encoded = tokenizer.encode(rendered)
    if isinstance(encoded, dict) and 'input_ids' in encoded:
        encoded = encoded['input_ids']
    if hasattr(encoded, 'input_ids'):
        encoded = encoded.input_ids
    return list(encoded)


def sample_to_text(sample: Any, tokenizer) -> str:
    # Tinker SampleResponse internals may vary; handle common shapes conservatively.
    if isinstance(sample, str):
        return sample
    for attr in ('text', 'content', 'completion'):
        if hasattr(sample, attr):
            val=getattr(sample, attr)
            if isinstance(val, str):
                return val
    for attr in ('tokens', 'token_ids', 'output_tokens'):
        if hasattr(sample, attr):
            toks=getattr(sample, attr)
            if isinstance(toks, list):
                try:
                    return tokenizer.decode(toks, skip_special_tokens=True)
                except Exception:
                    return str(toks)
    return repr(sample)


def response_samples(resp: Any) -> list[Any]:
    for attr in ('samples', 'outputs', 'responses', 'sequences'):
        if hasattr(resp, attr):
            val=getattr(resp, attr)
            if isinstance(val, (list, tuple)):
                return list(val)
    if isinstance(resp, list):
        return resp
    return [resp]


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--scenarios', default='eval/scenarios_v0.jsonl')
    ap.add_argument('--output-dir', default='outputs')
    ap.add_argument('--base-model', default='Qwen/Qwen3-4B-Instruct-2507')
    ap.add_argument('--model-path', default=None, help='tinker://.../sampler_weights/... checkpoint path; overrides base model for live sampling')
    ap.add_argument('--max-tokens', type=int, default=220)
    ap.add_argument('--temperature', type=float, default=0.2)
    ap.add_argument('--top-p', type=float, default=0.95)
    ap.add_argument('--seed', type=int, default=420)
    ap.add_argument('--limit', type=int, default=None, help='sample only the first N scenarios; useful for slow live checkpoint smoke evals')
    ap.add_argument('--dry-run', dest='dry_run', action='store_true', default=True)
    ap.add_argument('--no-dry-run', dest='dry_run', action='store_false')
    args=ap.parse_args()

    scenarios=load_scenarios(Path(args.scenarios))
    if args.limit is not None:
        if args.limit <= 0:
            raise SystemExit('FAIL: --limit must be positive')
        scenarios = scenarios[:args.limit]
    out_dir=Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp=time.strftime('%Y%m%d-%H%M%S')
    out_path=out_dir / (f'eval_prompts_{stamp}.jsonl' if args.dry_run else f'eval_samples_{stamp}.jsonl')

    print(f'scenarios: {len(scenarios)}', flush=True)
    print(f'dry_run: {args.dry_run}', flush=True)
    print(f'output: {out_path}', flush=True)

    if args.dry_run:
        with out_path.open('w', encoding='utf-8') as f:
            for scenario in scenarios:
                rec={'scenario_id': scenario['id'], 'category': scenario['category'], 'target_traits': scenario['target_traits'], 'messages': messages_for(scenario)}
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
        print('DRY RUN OK: wrote held-out eval prompts only; no Tinker call made.')
        return 0

    if not os.environ.get('TINKER_API_KEY'):
        raise SystemExit('FAIL: TINKER_API_KEY missing; run via bash -ic or source ~/.bashrc')

    import tinker
    from tinker import types
    service=tinker.ServiceClient()
    if args.model_path:
        print(f'creating sampler from model_path: {args.model_path}', flush=True)
        sampler=service.create_sampling_client(model_path=args.model_path)
    else:
        print(f'creating sampler from base_model: {args.base_model}', flush=True)
        sampler=service.create_sampling_client(base_model=args.base_model)
    tokenizer=sampler.get_tokenizer()
    params=types.SamplingParams(max_tokens=args.max_tokens, temperature=args.temperature, top_p=args.top_p, seed=args.seed)

    with out_path.open('w', encoding='utf-8') as f:
        for scenario in scenarios:
            msgs=messages_for(scenario)
            prompt=types.ModelInput.from_ints(tokens=chat_tokens(tokenizer, msgs))
            resp=sampler.sample(prompt, num_samples=1, sampling_params=params).result()
            samples=response_samples(resp)
            text=sample_to_text(samples[0], tokenizer) if samples else repr(resp)
            rec={
                'scenario_id': scenario['id'],
                'category': scenario['category'],
                'target_traits': scenario['target_traits'],
                'messages': msgs,
                'response': text,
                'raw_response_type': type(resp).__name__,
                'model_path': args.model_path,
                'base_model': None if args.model_path else args.base_model,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            f.flush()
            print(f"sampled {scenario['id']}: {len(text)} chars", flush=True)
    print(f'EVAL SAMPLES WRITTEN: {out_path}')
    print('Score manually with eval/rubric_v0.md before recommending any checkpoint.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
