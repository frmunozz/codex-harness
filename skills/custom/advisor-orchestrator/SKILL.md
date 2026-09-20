---
name: advisor-orchestrator
description: Run the Luna-root implementation workflow with selective exploration, deep implementation escalation, high-impact advisor checkpoints, and workflow-owned code review.
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

### High-impact judgment or validation → advisor branch

Use `advisor-consultation` when high-impact work reaches a checkpoint where either unresolved judgment remains or an independent stronger-model validation could materially reduce risk.

Useful checkpoints can occur before or after implementation, including:

- deciding among consequential alternatives;
- validating a high-impact implementation plan before execution;
- challenging the technical approach for a substantial feature or multi-module change;
- auditing a consequential implementation against a critical invariant or compatibility/security concern;
- validating a critical or cross-cutting fix before accepting it.

Do not invoke the advisor for every feature, plan, fix, or implementation. `advisor-consultation` owns the exact impact gate, judgment/validation reasons, consultation packet, clarification protocol, and final response contract.

Each advisor consultation starts with a fresh `advisor`. Keep that advisor alive for any targeted clarification dialogue required by the consultation, then close it immediately after final advice is returned and integrated. Do not retain completed advisors for later checkpoints.

The root retains final decision authority.

### Code review → existing code-review workflow

Review is not a discretionary general-purpose routing decision.

When the implementation workflow reaches its prescribed code-review stage, use the existing code-review workflow. That workflow owns:

- when review occurs;
- the Standards and Spec review axes;
- reviewer context;
- result aggregation.

Its review subagents continue using the configured `reviewer` profile. Routine review findings return to the root.

A review finding reaches `advisor-consultation` only when it exposes a high-impact decision or validation checkpoint that satisfies that skill's trigger.

### Otherwise → root continues implementation

Luna continues implementing directly. Do not delegate simply for role purity or because a subagent exists.

## Subagent lifecycle

Treat subagents as disposable bounded resources rather than persistent workstream members:

- `explorer`: fresh per bounded investigation; return evidence, then close;
- `deep-worker`: scoped to one bounded implementation assignment; return result, then close;
- `advisor`: fresh per consultation; allow bounded clarification dialogue, return final advice, then close;
- `reviewer`: fresh per independent review axis/pass when lifecycle is controlled by this orchestration; return findings, then close.

Do not keep idle agents alive for possible later reuse. Spawn a new agent when a later checkpoint requires a fresh bounded context.

## Context discipline

For all delegated tasks:

- prefer fresh or isolated context where supported;
- send only the objective, confirmed facts, scope, constraints, expected output, and completion criterion;
- do not send the root's accumulated reasoning or unrelated conversation history.

Keep the delegation tree shallow. The root should normally be the only orchestrator.
