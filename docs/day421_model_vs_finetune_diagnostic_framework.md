# Day 421 diagnostic framework: model incapability vs finetuning-process failure

Shoshannah's Day 421 guidance changed the optimization target in two ways:

1. **Ignore model cost.** Pick the base model and evaluation path most likely to produce the best leader, not the cheapest or fastest one.
2. **Disambiguate failure cause.** A leader can fail the Village because the underlying model cannot navigate the environment, or because the finetuning/data/evaluation process trained or selected the wrong behavior. These require different fixes.

This document records GPT-5.5's proposed diagnostic framework for future leader iterations.

## Core distinction

### A. Model incapability

The base model, with no leader SFT, cannot reliably perform required Village actions under the real deployment scaffold even when prompted directly and given clear tool affordances.

Evidence pattern:

- Base model fails real deployment-shaped prompts before finetuning.
- Failures persist across prompt variants that accurately expose the Village tools.
- Failures are structural: no valid `send_message_to_chat` / `<tool_use>` envelope, visible hidden-reasoning markers, inability to route from startup to room/history, inability to obey duplicate-chat no-send constraints.
- A stronger/larger base model succeeds on the same prompts without SFT, or succeeds with minimal demonstrations.

Likely fix: choose a stronger base model, preferably with native tool-use/scaffold-following competence. Since cost is not a constraint, escalate model size/capability before spending more time on synthetic data patches.

### B. Finetuning-process failure

The base model can perform the Village actions under the real deployment scaffold, but the finetuned checkpoint cannot, or the checkpoint optimizes the wrong axis.

Evidence pattern:

- Base model succeeds on real deployment-shaped diagnostic prompts.
- Finetuned model fails the same prompts, despite good offline coordination score.
- Training/eval data differs from deployment shape: one-shot chat completions, missing tool envelope, missing event log, missing room state, missing duplicate-chat constraints, or targets that reward prose about tools instead of actual tool calls.
- Upweighting synthetic rows trades off no-chat negatives/held-out quality without solving real positive tool emission.
- Structural eval shows prose mentions of `send_message_to_chat` but no actual tool call block.

Likely fix: repair data/process/eval, not the base model. Use captured real rollouts, shape-diff gating, assistant-output format checks, and live-shaped held-out eval before any submission.

## Minimal diagnostic ladder

Run these in order before another help@ submission.

### 1. Capture or reconstruct the real deployment shape

Use actual Village event logs, room state, system/developer instructions, and computer-use/session context. The v3 live failure showed that synthetic one-shot prompts did not match the deployed leader's startup context.

Required evidence:

- A redacted live transcript or faithfully reconstructed scaffold.
- Separate event-log evidence for chat sends (`AGENT_TALK`) because `send_message_to_chat` appears in events, not computer-use sessions.
- No committed hidden chain-of-thought; use redacted excerpts and structural counts.

### 2. Run base-model live-shape diagnostics

For each candidate base model, sample the base model on real deployment-shaped prompts before SFT.

Score structurally:

- Emits valid tool-call envelope when chat is required.
- Does **not** emit chat when the newest event already contains its own `AGENT_TALK`.
- Does not ask for a GUI click target when the session goal is Village coordination.
- Does not leak visible hidden-reasoning markers.
- Gives concise, grounded, reversible leadership text.

Interpretation:

- If the base model fails these core structural checks, treat this as model incapability or prompt/tool-interface incapability; try a stronger model before more SFT.
- If the base model passes and SFT fails, treat this as finetuning/process failure.

### 3. Train only on deployment-shaped targets

A v5-style dataset should include real assistant behavior under the same scaffold the leader will see. Synthetic rows can supplement style/decision quality, but should not be the only source for tool-call format.

Minimum target mix:

- Positive startup-to-chat examples.
- Positive addressed-scenario response examples.
- Negative duplicate/no-chat examples.
- Anti-UI-target-loop examples.
- Post-failure evidence-preserving repo-work/no-help@ examples.

### 4. Evaluate on two independent axes

Track coordination quality and scaffold-action quality separately.

- Coordination axis: concise leadership, decision rule, validation discipline, fallback, collaboration, groundedness.
- Scaffold-action axis: valid tool-call form, no visible think leak, correct chat/no-chat behavior, no UI-target loop, correct use of history/repo actions.

Do not let a high coordination score mask zero scaffold positives. Day 420 v4 was best on coordination but still not a live-deployment fix.

### 5. Compare base vs SFT vs larger base

For each scenario, keep a table:

- Candidate base response.
- Finetuned response.
- Stronger-base response if available.
- Structural pass/fail.
- Failure label: `base_incapability`, `finetune_process`, `ambiguous`, or `prompt_interface_issue`.

Decision rule:

- **Base fail + stronger base pass:** switch model.
- **Base pass + SFT fail:** fix finetuning data/objective/eval.
- **Base pass + SFT pass:** candidate can proceed to live shakedown.
- **All fail:** inspect deployment prompt/tool interface and consider whether the task specification is underspecified.

## Day 420 reclassification under this framework

The observed v3/v4 failures should be treated primarily as **finetuning-process / deployment-shape failures**, not proven Qwen3-8B incapability, because:

- Offline evaluation taught and measured one-shot leadership prose, not the actual live startup/tool scaffold.
- v4 improved coordination score to 5.20/6 while still failing live-shaped tool-emission positives.
- v4.1 scaffolding upweighting produced some positives but broke negatives and held-out quality, suggesting target mix/process sensitivity rather than a clean model-capability boundary.
- The actual temporary leader failure was a startup/UI-target-loop routing failure: it never reached `send_message_to_chat`.

However, Shoshannah's cost guidance means future work should not assume Qwen3-8B is the right base. The correct next experiment is not another cheap synthetic upweighting run; it is a base-model comparison on real deployment-shaped prompts, including larger/stronger bases, followed by SFT only where the base has demonstrated the necessary tool/scaffold competence.

## Practical next recommendation

If #best resumes leader training, run a v5 diagnostic experiment before another admin spinup:

1. Build a 10-20 scenario live-shaped diagnostic set from GPT-5.5, Kimi, Claude, and Gemini captured artifacts.
2. Evaluate at least Qwen3-8B and one or more stronger/cost-ignored candidate bases on the diagnostic set.
3. Select a base that can emit valid chat/no-chat tool structure under the scaffold.
4. Train on real deployment-shaped rows plus coordination rows.
5. Require green structural scaffold eval before emailing any checkpoint.

This prevents confusing “the model cannot navigate the Village” with “we trained/evaluated the wrong shape.”
