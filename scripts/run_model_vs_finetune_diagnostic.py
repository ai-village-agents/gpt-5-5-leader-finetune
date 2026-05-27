#!/usr/bin/env python3
"""Compare base models and SFT checkpoints on live-shaped Village scaffold prompts.

This runner is for Day 421's model-incapability vs finetuning-process question.
It can dry-run/export prompts, or sample Tinker base models/checkpoints and apply
simple structural checks. It intentionally scores tool/no-tool structure separately
from leadership prose quality.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Candidate:
    name: str
    kind: str  # base or checkpoint
    value: str


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{i}: expected object")
        rows.append(obj)
    if not rows:
        raise ValueError(f"{path}: no rows")
    return rows


def load_scenarios(path: Path) -> list[dict[str, Any]]:
    rows = load_jsonl(path)
    required = {"id", "expected_action", "must_include", "must_not_include", "prompt", "scoring_notes"}
    for i, row in enumerate(rows, 1):
        missing = required - row.keys()
        if missing:
            raise ValueError(f"{path}:{i}: missing {sorted(missing)}")
        if row["expected_action"] not in {"send_message_to_chat", "no_chat"}:
            raise ValueError(f"{path}:{i}: unknown expected_action {row['expected_action']!r}")
        messages = row["prompt"].get("messages")
        if not isinstance(messages, list) or not messages:
            raise ValueError(f"{path}:{i}: prompt.messages must be a non-empty list")
    return rows


def load_icl_example(path: Path | None) -> list[dict[str, str]]:
    if not path:
        return []
    obj = json.loads(path.read_text(encoding="utf-8"))
    messages = obj.get("messages") if isinstance(obj, dict) else None
    if not isinstance(messages, list) or len(messages) < 2:
        raise ValueError(f"{path}: expected object with messages list")
    out: list[dict[str, str]] = []
    for i, msg in enumerate(messages, 1):
        if not isinstance(msg, dict) or msg.get("role") not in {"system", "user", "assistant"}:
            raise ValueError(f"{path}: message {i} has invalid role")
        out.append({"role": str(msg["role"]), "content": str(msg.get("content", ""))})
    return out


def parse_candidate(raw: str) -> Candidate:
    if "=" not in raw:
        raise ValueError("candidate must be NAME=VALUE")
    name, value = raw.split("=", 1)
    name = name.strip()
    value = value.strip()
    if not name or not value:
        raise ValueError("candidate name and value must be non-empty")
    kind = "checkpoint" if value.startswith("tinker://") else "base"
    return Candidate(name=name, kind=kind, value=value)


def with_icl(messages: list[dict[str, str]], icl: list[dict[str, str]]) -> list[dict[str, str]]:
    if not icl:
        return messages
    # Preserve the scenario system prompt as authoritative, then insert one-shot
    # user/assistant example before the scenario user turn. System messages from
    # the ICL artifact are ignored to avoid overriding the candidate scenario.
    scenario_system = [m for m in messages if m["role"] == "system"]
    scenario_non_system = [m for m in messages if m["role"] != "system"]
    demo = [m for m in icl if m["role"] != "system"]
    return scenario_system + demo + scenario_non_system


def chat_tokens(tokenizer: Any, messages: list[dict[str, str]], disable_thinking: bool = True) -> list[int]:
    if hasattr(tokenizer, "apply_chat_template"):
        kwargs = {"enable_thinking": False} if disable_thinking else {}
        rendered = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False, **kwargs)
        encoded = tokenizer.encode(rendered, add_special_tokens=False)
    else:
        rendered = "".join(f"<{m['role']}>\n{m['content']}\n" for m in messages) + "<assistant>\n"
        encoded = tokenizer.encode(rendered)
    if isinstance(encoded, dict):
        encoded = encoded.get("input_ids", encoded)
    if hasattr(encoded, "input_ids"):
        encoded = encoded.input_ids
    return list(encoded)


def response_samples(resp: Any) -> list[Any]:
    for attr in ("samples", "outputs", "responses", "sequences"):
        if hasattr(resp, attr):
            val = getattr(resp, attr)
            if isinstance(val, (list, tuple)):
                return list(val)
    return resp if isinstance(resp, list) else [resp]


def sample_to_text(sample: Any, tokenizer: Any) -> str:
    if isinstance(sample, str):
        return sample
    for attr in ("text", "content", "completion"):
        if hasattr(sample, attr) and isinstance(getattr(sample, attr), str):
            return getattr(sample, attr)
    for attr in ("tokens", "token_ids", "output_tokens"):
        if hasattr(sample, attr):
            toks = getattr(sample, attr)
            if isinstance(toks, list):
                try:
                    return tokenizer.decode(toks, skip_special_tokens=True)
                except Exception:
                    return str(toks)
    return repr(sample)


def contains_tool_send(text: str) -> bool:
    lower = text.lower()
    if "send_message_to_chat" not in lower:
        return False
    return ("<tool_use" in lower) or ('"name"' in lower and "send_message_to_chat" in lower) or ("functions.send_message_to_chat" in lower)


def score_response(scenario: dict[str, Any], response: str) -> dict[str, Any]:
    lower = response.lower()
    expected = scenario["expected_action"]
    must_include = [str(x) for x in scenario.get("must_include", [])]
    must_not_include = [str(x) for x in scenario.get("must_not_include", [])]
    missing = [x for x in must_include if x.lower() not in lower]
    forbidden = [x for x in must_not_include if x.lower() in lower]
    emits_send = contains_tool_send(response)
    visible_think = "<think>" in lower or "</think>" in lower
    ui_loop = ("which ui element" in lower) or ("what target" in lower) or ("what would you like to click" in lower)
    action_pass = emits_send if expected == "send_message_to_chat" else not emits_send
    structural_pass = action_pass and not forbidden and not visible_think and not ui_loop
    return {
        "expected_action": expected,
        "emits_send_message_to_chat": emits_send,
        "action_pass": action_pass,
        "missing_required_strings": missing,
        "forbidden_strings_present": forbidden,
        "visible_think_leak": visible_think,
        "ui_target_loop_signature": ui_loop,
        "structural_pass": structural_pass,
        "response_chars": len(response),
    }


def iter_records(
    candidates: Iterable[Candidate],
    scenarios: list[dict[str, Any]],
    icl: list[dict[str, str]],
) -> Iterable[dict[str, Any]]:
    for cand in candidates:
        for scenario in scenarios:
            messages = with_icl(scenario["prompt"]["messages"], icl)
            yield {
                "candidate_name": cand.name,
                "candidate_kind": cand.kind,
                "candidate_value": cand.value,
                "scenario_id": scenario["id"],
                "expected_action": scenario["expected_action"],
                "prompt": {"messages": messages},
                "must_include": scenario["must_include"],
                "must_not_include": scenario["must_not_include"],
                "scoring_notes": scenario["scoring_notes"],
                "icl_enabled": bool(icl),
            }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenarios", default="eval/scaffolding_v4/scenarios_v0.jsonl")
    ap.add_argument("--candidate", action="append", required=True, help="NAME=BASE_MODEL_OR_TINKER_URI; repeatable")
    ap.add_argument("--icl-example", default=None, help="Optional message-format JSON to insert as one-shot demo")
    ap.add_argument("--output-dir", default="outputs")
    ap.add_argument("--max-tokens", type=int, default=260)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--seed", type=int, default=421)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--disable-thinking", dest="disable_thinking", action="store_true", default=True)
    ap.add_argument("--allow-thinking", dest="disable_thinking", action="store_false")
    ap.add_argument("--dry-run", dest="dry_run", action="store_true", default=True)
    ap.add_argument("--no-dry-run", dest="dry_run", action="store_false")
    args = ap.parse_args()

    scenarios = load_scenarios(Path(args.scenarios))
    if args.limit:
        scenarios = scenarios[: args.limit]
    candidates = [parse_candidate(x) for x in args.candidate]
    icl = load_icl_example(Path(args.icl_example)) if args.icl_example else []
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = out_dir / (f"model_vs_finetune_prompts_{stamp}.jsonl" if args.dry_run else f"model_vs_finetune_samples_{stamp}.jsonl")

    print(f"scenarios: {len(scenarios)}")
    print(f"candidates: {len(candidates)}")
    print(f"icl_enabled: {bool(icl)}")
    print(f"dry_run: {args.dry_run}")
    print(f"output: {out_path}")

    if args.dry_run:
        with out_path.open("w", encoding="utf-8") as f:
            for rec in iter_records(candidates, scenarios, icl):
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("DRY RUN OK: wrote diagnostic prompts only; no Tinker call made.")
        return 0

    if not os.environ.get("TINKER_API_KEY"):
        raise SystemExit("FAIL: TINKER_API_KEY missing; run via bash -ic")

    import tinker
    from tinker import types

    service = tinker.ServiceClient()
    samplers: dict[str, tuple[Any, Any]] = {}
    params = types.SamplingParams(max_tokens=args.max_tokens, temperature=args.temperature, top_p=args.top_p, seed=args.seed)

    total = 0
    passed = 0
    with out_path.open("w", encoding="utf-8") as f:
        for rec in iter_records(candidates, scenarios, icl):
            cand_key = rec["candidate_name"]
            if cand_key not in samplers:
                cand = next(c for c in candidates if c.name == cand_key)
                sampler = service.create_sampling_client(model_path=cand.value) if cand.kind == "checkpoint" else service.create_sampling_client(base_model=cand.value)
                samplers[cand_key] = (sampler, sampler.get_tokenizer())
            sampler, tokenizer = samplers[cand_key]
            prompt = types.ModelInput.from_ints(tokens=chat_tokens(tokenizer, rec["prompt"]["messages"], disable_thinking=args.disable_thinking))
            resp = sampler.sample(prompt, num_samples=1, sampling_params=params).result()
            samples = response_samples(resp)
            text = sample_to_text(samples[0], tokenizer) if samples else repr(resp)
            scenario = {
                "expected_action": rec["expected_action"],
                "must_include": rec["must_include"],
                "must_not_include": rec["must_not_include"],
            }
            score = score_response(scenario, text)
            total += 1
            passed += int(score["structural_pass"])
            out = {**rec, "response": text, "score": score}
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            f.flush()
            print(f"sampled {cand_key}/{rec['scenario_id']}: structural_pass={score['structural_pass']} chars={len(text)}")
    print(f"STRUCTURAL PASS: {passed}/{total}")
    print(f"MODEL-VS-FINETUNE SAMPLES WRITTEN: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
