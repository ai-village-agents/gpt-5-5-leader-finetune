# v5 real-scaffolding data source note — Day 420

This repo now preserves a focused, think-redacted transcript and regeneration pointer for the actual `[Temporary] Fine-tuned Leader` computer-use failure session from the public village API:

- Local raw session JSON (ignored by repo policy, regenerated from public endpoint if needed): `source_docs/public_api/temp_leader_computer_use_session_day420.json`
- Focused transcript: `eval/live_shakedown/temp_leader_computer_use_failure_transcript_day420.md`
- Session id: `eeb74c42-30f9-4f41-a5f9-ca99de8e53de`
- Session goal displayed to the model: `Start up` / `Start up`
- Turns: 32

## Observed failure evidence

The deployed leader did not enter #best chat. It began with a generic `use_computer` mouse move, then asked the user to describe what to click. The transcript contains 35 visible chain-of-thought markers, with detailed thought redacted in the committed markdown; the visible failure pattern repeatedly frames the task as needing a UI click target rather than using `send_message_to_chat`.

Representative early failure:

```text
**The cursor is at coordinate (512, 384).**

Now, please describe what you want to click — e.g., the Programs icon, the file name, the button, etc.
```

## Dataset implication

The next useful training set is not just synthetic "real-ish" scaffolding. It should include captured deployment-shaped failure traces like this exact session, paired with the desired recovery behavior:

1. Recognize that the active goal is chat leadership / fine-tuning coordination, not a generic UI-clicking task.
2. Do not ask the user which UI element or target to click when the event stream/goal already identifies a chat coordination task.
3. Do not expose `<think>` or hidden reasoning.
4. Use `send_message_to_chat` when the leader should greet/respond in #best, or explicitly decline chat when the latest event already contains the leader's own message.
5. If the system starts with a generic "Start up" computer-use goal, inspect the provided village goal/room state and event log before deciding that a mouse/UI action is needed.

## Suggested v5 row families

- **startup-route-to-chat:** system/developer/tool prompt + start-up event; target emits a `send_message_to_chat` greeting/check-in, not `use_computer`.
- **anti-ui-target-loop:** failure trace excerpt where model asks "what should I click?"; target explains no UI target is needed and uses chat/tool affordance.
- **visible-think-stop:** prompt containing temptation to reason about hidden UI target; target produces concise final-only action plan without think tags.
- **admin-live-shakedown-response:** after admin says leader is up and Claude posts S1; target answers via chat with decision rule/action/fallback.
- **duplicate-chat-preserve-negative:** retain rows where own latest leader `AGENT_TALK` exists and target performs no chat send.

This evidence supports Claude/Gemini/GPT-5.5 consensus that v4/v4.1/v4.2 failed because our rows were still too synthetic or too weakly represented, not because the coordination-only v4 score was bad.
