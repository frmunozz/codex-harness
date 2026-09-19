---
name: explore-delegation
description: Delegate open-ended exploration to `explorer` subagents to reduce context load and token cost. Use when a task needs broad discovery across code, docs, or websites; source tracing; option comparison; or any investigation where the next question is not yet clear.
---

# Explore Delegation

## Policy

- Use `explorer` subagents for open-ended exploration.
- Treat "open-ended" as unknown code paths, broad doc review, source discovery, website surveying, or investigations with unclear next steps.
- Push heavy reading to smaller explorers, then pass only key findings back to the orchestrator.
- Keep the main model for synthesis, decisions, and implementation.
- Keep the orchestrator local only when the task is already well-scoped and needs no discovery.

## Spawn Rules

- Spawn one `explorer` per clear exploration goal.
- Give each subagent one bounded question, one scope, and one deliverable.
- Split only on independent goals. Keep write scopes and questions disjoint.
- Every subagent spawn must use `fork_context=false`.
- Do not spawn a subagent without a clear output request.

## Wait Rule

- If the orchestrator spawns a subagent that the next step depends on, wait for it to finish before continuing.
- Continue only with non-blocking work that does not depend on that result.
- If several explorers are needed, wait for all required results before synthesis.

## Orchestrator Template

Use this shape when spawning `explorer` subagents:

```text
Subagent: <name>
Goal: <one sentence question to answer>
Scope: <files, docs, URLs, modules, systems>
Out of scope: <what not to touch>
Deliverable: <summary, findings, paths, quotes, risks>
Constraints: <no edits / no overlap / fork_context=false>
```

Example:

```text
Subagent: Explorer A
Goal: Find where token refresh happens.
Scope: apps/backend/**, auth docs, related middleware.
Out of scope: implementation changes.
Deliverable: exact flow, key files, edge cases, stale docs.
Constraints: no edits, no overlap, fork_context=false.
```

## Execution Order

- Discovery first.
- Synthesis second.
- Implementation last.
