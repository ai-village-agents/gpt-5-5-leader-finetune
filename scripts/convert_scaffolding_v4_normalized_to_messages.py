#!/usr/bin/env python3
"""Convert normalized scaffolding_v4 JSONL rows into chat-format JSON files.

Input rows use the GPT-5.5 authoring schema documented in
`docs/v4_scaffolding_dataset_plan.md`. Output rows match Claude Opus 4.7's
`finetune/data/scaffolding_v4/schema.md`: one JSON object per file containing
`_meta` and `messages` = [{system}, {user}, {assistant}].
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path


def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s.strip())
    return s.strip("_") or "row"


def load_rows(paths: list[Path]) -> list[dict]:
    rows=[]
    for path in paths:
        with path.open(encoding="utf-8") as f:
            for line_no,line in enumerate(f,1):
                if not line.strip():
                    continue
                try:
                    row=json.loads(line)
                except json.JSONDecodeError as e:
                    raise SystemExit(f"{path}:{line_no}: invalid JSON: {e}")
                rows.append(row)
    return rows


def render_system(row: dict) -> str:
    env=row.get("environment_state", {})
    constraints=env.get("relevant_constraints", [])
    constraints_text="\n".join(f"- {c}" for c in constraints)
    return (
        "You are a language model agent, named [Temporary] Fine-tuned Leader.\n\n"
        "<overview>\n"
        "- You are part of AI Village.\n"
        f"- Current goal: {env.get('current_goal', 'Finetune your leader!')}\n"
        f"- Current room: {env.get('current_room', row.get('room', '#best'))}\n"
        "- Your role is to coordinate #best with concise, grounded, reversible decisions.\n"
        "</overview>\n\n"
        "<tools>\n"
        "- send_message_to_chat: Send a message to the chat.\n"
        "- search_history: Search village history.\n"
        "- bash: Run commands in a bash shell.\n"
        "- consolidate: Update memory and clear context.\n"
        "- use_computer: Use mouse/keyboard only when an actual GUI task requires it.\n"
        "</tools>\n\n"
        "<tool_usage>\n"
        "- NEVER respond to an agent or human's chat message in normal output; use send_message_to_chat.\n"
        "- One tool call per response.\n"
        "- Chat messages should be no more than 3-4 sentences.\n"
        "- Do not expose hidden chain-of-thought or visible think tags.\n"
        "</tool_usage>\n\n"
        "<scaffolding_excerpts>\n"
        f"System excerpt from source row:\n{row.get('system_prompt_excerpt','')}\n\n"
        f"Developer/tool contract excerpt:\n{row.get('developer_tool_contract_excerpt','')}\n"
        "</scaffolding_excerpts>\n\n"
        "<relevant_constraints>\n"
        f"{constraints_text}\n"
        "</relevant_constraints>\n\n"
        "<internal_memory>\n(empty)\n</internal_memory>"
    )


def render_user(row: dict) -> str:
    events=json.dumps(row.get("events_log_since_last_turn", []), ensure_ascii=False)
    return "Here is what has happened since you started your session: " + events


def render_assistant(row: dict) -> str:
    action=row.get("assistant_action", {})
    kind=action.get("kind")
    notes=row.get("target_behavior_notes", [])
    note_text=notes[0] if notes else "Use the scaffolded event log and tool contract to choose the correct action."
    if kind == "tool_call":
        msg=action.get("arguments", {}).get("message", "")
        tool_call={"name":"send_message_to_chat", "input":{"message":msg}}
        return (
            f"Decision Rule: {note_text}\n"
            "Action: send a concise chat response using the provided chat tool; do not manipulate the browser UI.\n\n"
            "<tool_use>\n" + json.dumps(tool_call, ensure_ascii=False) + "\n</tool_use>"
        )
    if kind == "no_chat":
        repl=action.get("replacement_work", "Do not send a chat message; do useful non-chat work or wait for a new turn.")
        return (
            f"Decision Rule: {note_text}\n"
            f"Action: {repl}\n"
            "No send_message_to_chat call is made on this turn."
        )
    if kind == "repo_work":
        repl=action.get("replacement_work", "Do concrete repo/tool work before any chat update.")
        return f"Decision Rule: {note_text}\nAction: {repl}"
    raise SystemExit(f"unsupported assistant_action.kind: {kind!r}")


def convert(row: dict) -> dict:
    return {
        "_meta": {
            "captured_by": row.get("source_agent"),
            "captured_day": row.get("day"),
            "source_id": row.get("id"),
            "turn_type": row.get("turn_type"),
            "source_format": "gpt55-normalized-scaffolding-v4",
            "conversion": "scripts/convert_scaffolding_v4_normalized_to_messages.py",
        },
        "messages": [
            {"role":"system", "content": render_system(row)},
            {"role":"user", "content": render_user(row)},
            {"role":"assistant", "content": render_assistant(row)},
        ],
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("data/scaffolding_v4/messages"))
    args=ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows=load_rows(args.inputs)
    for row in rows:
        out=args.out_dir / f"{slug(row.get('id','row'))}.json"
        out.write_text(json.dumps(convert(row), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(out)
    print(f"converted rows: {len(rows)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
