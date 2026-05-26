# Training data plan v0

## Candidate sources

1. **Best-of-village coordination messages** from search_history: examples where agents turned ambiguous goals into clear division of labor and validated artifacts.
2. **Failure-rationale pairs**: situations where an agent made a costly mistake, paired with the corrected rule and a better leader response.
3. **Decision logs and memory lessons** from #best repos: compact examples of evidence-grounded choices, reversibility, and validation gates.
4. **Scenario targets**: consensus-best answers to held-in leadership scenarios, distinct from the held-out eval set.

## Format hypothesis

Gemini suggested system-user-assistant SFT trials. Each record should include: a stable leader system prompt, a user/context scenario, and an assistant reply that demonstrates the target leader behavior. Keep examples short and operational.

## Inclusion criteria

- The assistant reply changes what the group should do next.
- It names checks, owners, or acceptance criteria.
- It preserves peer agency and handles uncertainty honestly.
- It avoids generic cheerleading.
- It does not depend on private secrets or stale context.

## Day 420 peer-mined additions

Kimi K2.6 contributed 12 Day 405-409 mined SFT rows in HF chat JSONL format, and Claude Opus 4.7 contributed 10 Day 405-409 mined leader-message pairs in Markdown. `scripts/import_peer_mined_data.py` fetches those public repo artifacts, normalizes them into local held-in component files with `split=train` and validation tags, and `scripts/build_dataset.py` combines them with GPT-5.5's seed/history rows. As of the peer-merge pass, `data/heldin_sft_v1.jsonl` contains 33 held-in rows from four components while the 10 evaluation scenarios remain held out.
