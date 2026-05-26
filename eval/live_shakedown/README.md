# Live shakedown results

Use this directory only after `[Temporary] Fine-tuned Leader` is confirmed configured.

Protocol: `docs/live_shakedown_protocol_day420.md`.

Recommended files once testing starts:

- `leader_sft_v3_live_samples.jsonl`: one JSON object per prompted scenario with raw response and structural flags.
- `leader_sft_v3_live_scores.jsonl`: one JSON object per scenario with manual 0-2 score fields and notes.
- `leader_sft_v3_live_summary.md`: concise keep/iterate recommendation and #best vote evidence.

Do not fabricate samples. If no leader response has occurred yet, leave only this README and the template file.
