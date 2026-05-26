# v4 scaffolding-shaped leader dataset plan — Day 420

Status: draft GPT-5.5 contribution after the live `leader-sft-v3` deployment failed.

## Why v4 is needed

The selected `leader-sft-v3` checkpoint sampled cleanly through the Tinker API, but the deployed `[Temporary] Fine-tuned Leader` did not speak in `#best`. The public village activity showed it stuck in startup/computer-use framing, apparently reasoning about UI targets instead of parsing the village scaffold and using `send_message_to_chat`.

The likely failure is **dataset shape mismatch**:

- v3 taught short one-shot leadership prompts: `system + user -> assistant coordination answer`.
- the real village agent receives long system/developer/tool instructions, current room state, event updates, memory/context, and tool-call affordances.
- the leader must decide when to answer with `send_message_to_chat`, when to work in repos/tools, and when not to chat.

## Proposed v4 row shape

Each row should be one normalized real or realistic deployment-shaped trajectory:

```json
{
  "id": "unique-row-id",
  "source_agent": "GPT-5.5",
  "day": 420,
  "room": "#best",
  "turn_type": "positive_chat_tool_call | negative_no_chat | negative_wrong_frame | positive_repo_work_then_chat",
  "system_prompt_excerpt": "Short/redacted excerpt of durable role/tool instructions that matter for the behavior.",
  "developer_tool_contract_excerpt": "Short/redacted excerpt of tool semantics and chat rules.",
  "events_log_since_last_turn": [
    {"actionType":"AGENT_TALK", "agentName":"...", "content":"...", "createdAt":"..."}
  ],
  "environment_state": {
    "current_goal": "Finetune your leader!",
    "current_room": "#best",
    "available_chat_tool": "send_message_to_chat",
    "relevant_constraints": ["no visible chain-of-thought", "do not use browser/computer UI unless needed"]
  },
  "assistant_action": {
    "kind": "tool_call | no_chat | repo_work",
    "tool_name": "send_message_to_chat",
    "arguments": {"message": "..."}
  },
  "target_behavior_notes": ["Why this is the right action in the scaffold."],
  "anti_behavior_notes": ["What wrong behavior this row should suppress."]
}
```

## Inclusion guidance

Prefer rows that teach the deployed model to:

1. Parse the event log as the immediate user-visible context.
2. Treat direct mentions in `#best` as candidates for concise `send_message_to_chat` responses.
3. Avoid browser/UI target-seeking when the task is a chat/tool coordination turn.
4. Do concrete repo/tool work before status updates when possible.
5. Suppress visible `<think>` / hidden chain-of-thought markers.
6. Obey duplicate-chat safeguards: if an event update already contains the agent's own message, do not send another.

Minimum v4 seed target: one high-quality row from each #best agent, then 4-8 additional rows covering negative/wrong-frame and duplicate-chat cases.

## GPT-5.5 initial contribution

`data/scaffolding_v4/gpt55_scaffolding_example_v0.jsonl` contains one deployment-shaped row from the post-failure schema-coordination turn. It is normalized/redacted rather than a full raw prompt dump, but preserves the critical scaffold shape: system/developer role excerpts, event-log messages directed at GPT-5.5, and the intended `send_message_to_chat` action.
