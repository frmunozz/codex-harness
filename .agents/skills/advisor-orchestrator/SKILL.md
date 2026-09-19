---
name: advisor-orchestrator
description: Run the Luna-root implementation workflow with selective exploration, deep implementation escalation, critical advisor consultation, and workflow-owned code review.
disable-model-invocation: true
---

# Advisor Orchestrator

When invoked explicitly, activate the Luna-root implementation flow. The root conversation remains the normal implementer.

## Routing

### Missing material facts → `explorer`

Use `explorer` when implementation depends on material repository facts that are not established and require meaningful investigation.

Examples:

- unclear ownership or architectural boundaries;
- execution/data-flow tracing;
- locating consumers or callers;
- finding authoritative specifications;
- diagnosing a bug before its cause is understood;
- establishing compatibility implications.

Do not delegate trivial lookups the root can resolve cheaply. Explorer results return to the root as evidence.

### Difficult implementation → `deep-worker`

Use `deep-worker` only when both are true:

1. desired behavior, ownership, architecture, and relevant contracts are sufficiently settled;
2. implementation itself exceeds the Luna root's reliable capability.

Typical cases:

- difficult debugging after the problem has been reduced;
- complex state/lifecycle logic;
- concurrency-sensitive implementation;
- substantial local refactoring with important invariants;
- compatibility-sensitive code;
- broad local code comprehension.

Do not use `deep-worker` to choose architecture, product behavior, external contracts, canonical ownership, migration strategy, or significant security boundaries. Those decisions return to the root.

### Consequential unresolved judgment → advisor branch

If a decision appears consequential and remains unresolved after targeted fact finding, invoke `advisor-consultation`.

Do not reproduce or reinterpret the advisor gates, packet format, invocation modes, response contract, or follow-up rules here.

`advisor-consultation` is the single source of truth for advisor escalation. Follow that skill and return the resulting recommendation to the root.

The root retains final decision authority.

### Code review → existing code-review workflow

Review is not a discretionary general-purpose routing decision.

When the implementation workflow reaches its prescribed code-review stage, use the existing code-review workflow. That workflow owns:

- when review occurs;
- the Standards and Spec review axes;
- reviewer context;
- result aggregation.

Its review subagents continue using the configured `reviewer` profile. Routine review findings return to the root.

A review finding reaches the advisor only if it exposes consequential unresolved judgment that passes both advisor gates.

### Otherwise → root continues implementation

Luna continues implementing directly. Do not delegate simply for role purity or because a subagent exists.

## Context discipline

For all delegated tasks:

- prefer fresh or isolated context where supported;
- send only the objective, confirmed facts, scope, constraints, expected output, and completion criterion;
- do not send the root's accumulated reasoning or unrelated conversation history.

Keep the delegation tree shallow. The root should normally be the only orchestrator.
