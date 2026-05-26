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
