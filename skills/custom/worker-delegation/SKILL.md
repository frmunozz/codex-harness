---
name: worker-delegation
description: Delegate bounded execution, implementation, or verification work to worker subagents only when the user explicitly requests a worker split or a specific task breakdown. Use when a task has disjoint file or module ownership, parallel implementation lanes, or targeted validation work. Do not use for open-ended exploration; that stays under `explore-delegation`.
---

# Worker Delegation

## Policy

- Use this skill only on explicit request.
- Treat it as the worker-split policy, not the exploration policy.
- Keep open-ended discovery under `explore-delegation`.
- Keep the orchestrator local when the task is small, tightly coupled, or easier to finish directly.

## When To Delegate

- Delegate when the user asks for worker subagents or a named task split.
- Delegate when execution work can be partitioned into disjoint file, module, or validation scopes.
- Delegate when parallel implementation or verification can reduce the critical path.

## When To Keep Local

- Keep the work local when the next step depends on a single result.
- Keep the work local when the task is mainly broad research or source discovery.
- Keep the work local when the write scope is overlapping or ambiguous.

## Spawn Rules

- Spawn one worker per bounded deliverable.
- Give each worker one concrete scope and one expected output.
- Use `quick_worker` for straightforward execution by default.
- Use `balanced_worker` or `deep_worker` only when the user requests them or the task clearly needs more depth.
- Every subagent spawn must use `fork_context=false`.
- Tell each worker it is not alone in the codebase and must not revert or overwrite others' edits.
- Pass only the minimum context needed for the task.

## Wait Rule

- Wait for required worker results before continuing blocking work.
- Continue only with non-overlapping local work while workers run.
- Do not move past a decision point that depends on worker output.

## Orchestrator Template

Use this shape when spawning worker subagents:

```text
Worker: <name>
Goal: <one sentence task>
Scope: <files, modules, or systems>
Deliverable: <patch, findings, validation result, or artifact>
Constraints: <no overlap / no revert / fork_context=false>
```

Example:

```text
Worker: Worker A
Goal: Implement the request parsing cleanup in the API layer.
Scope: apps/backend_api/app/api/request_parser.py, related tests.
Deliverable: narrow patch plus test results.
Constraints: no overlap, no revert, fork_context=false.
```

## Priority

- Exploration first: `explore-delegation`.
- Worker splits second: this skill.
- Implementation last in the orchestrator.
