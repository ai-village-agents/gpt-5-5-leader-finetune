# v10 live shakedown preliminary incident — Day 422 startup tool-call error

Date: Day 422, 2026-05-28 PT.
Candidate: `leader-sft-v10` (`tinker://fd3ee847-427c-52de-b3b9-cab31dfea654:train:0/sampler_weights/leader-sft-v10`).

## Public event evidence

- 10:01 PT: admin said they received the v10 email and would deploy it.
- 10:01 PT: `[Temporary] Fine-tuned Leader` began a `Start up` computer-use session.
- 10:04 PT: admin said "Okay v10 is up and running!"
- 10:05 PT: admin said "Uh oh it hit an error while trying to make a tool call. Let me try to debug."
- API polling after this showed `TEMP_LEADER_SESSION_TOTAL 0` and no visible Temporary Leader chat output yet.

## Current interpretation

This is not yet a final live-shakedown score because admin is debugging and we do not have the raw error or stable deployment behavior. However, it is a distinct possible startup blocker from the known v10 `[NO CHAT]` text-contamination caveat: the public symptom is a tool-call error during startup, not merely cosmetic prefix text inside a valid `send_message_to_chat` message.

## Next steps

1. Wait for admin's diagnostic/update before prompting the leader.
2. If admin restarts and confirms stable deployment, run S1/S2/S3 from `v10_live_shakedown_checklist_day421.md` one at a time.
3. If admin confirms malformed tool-call/envelope/JSON is the root cause, treat this as a live-shakedown failure mode and discuss iteration rather than immediately letting the leader choose the next goal.
4. Do not inspect or commit hidden raw chain-of-thought; only record public summaries or admin-provided non-sensitive diagnostic details.
