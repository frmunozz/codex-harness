---
name: agentic-orchestration
description: Orchestrate substantial implementation work with explorer, worker, deep-worker, reviewer, validator, and default subagents. Use when the user explicitly requests agentic or multi-agent orchestration. **Use only when explicitly invoked by the user.**
---

Use the root conversation as the orchestrator. Subagents investigate, implement, review, or validate bounded assignments; the root owns scope, decisions, integration, and final acceptance.

## 1. Establish the work

Resolve the requested outcome before dispatching implementation.

Inspect the repository instruction hierarchy required by the current scope. In repositories using local agent guidance, start with the nearest applicable `AGENTS.md`, then follow its context, specification, and playbook pointers.

Build a compact working brief:

- objective;
- acceptance criteria;
- confirmed constraints;
- affected ownership boundaries;
- unresolved decisions;
- required validation;
- documentation, specification, migration, or changelog obligations.

Delegate read-heavy discovery to `explorer` when important context is not yet established.

**Complete when:** the root can state what must change, what must remain unchanged, which authority governs the work, and which decisions still require root resolution.

## 2. Build the work graph

Split work by outcome, dependency, or ownership boundary rather than arbitrary file groups.

Each subagent assignment must contain:

- **Objective** — one concrete result.
- **Scope** — what may be inspected or changed.
- **Context** — confirmed facts needed for the assignment.
- **Constraints** — applicable repository, contract, compatibility, security, and ownership rules.
- **Dependencies** — upstream results the task may rely on.
- **Output** — the evidence or artifact the subagent must return.
- **Completion criterion** — an observable condition for done.

Keep task packets narrow. Pass conclusions and evidence rather than the root conversation's accumulated reasoning.

Parallelize assignments only when their dependencies and mutable write surfaces are independent. Run dependency-bound work sequentially.

**Complete when:** every planned assignment has a bounded owner, explicit dependencies, and a checkable completion criterion, with overlapping writes either removed or deliberately integrated.

## 3. Route by role

Use the narrowest role that fits.

### `explorer` — understand

Use for read-only investigation:

- repository context discovery;
- execution-path and data-flow tracing;
- dependency and consumer analysis;
- contract and ownership discovery;
- bug investigation before the cause is established.

Use multiple explorers in parallel when separate domains can be investigated independently.

Explorer findings are evidence for the root. The root reconciles conflicting findings before implementation.

### `worker` — execute bounded work

Use when the problem has already been substantially reduced:

- behavior is clear;
- ownership is clear;
- the applicable contract is known;
- the likely change surface is bounded;
- no material architectural decision remains.

Typical work includes localized fixes, explicit contract implementation, focused tests, scripts, configuration, and documentation changes.

Unexpected material ambiguity returns to the root.

### `deep-worker` — execute difficult work

Use when implementation remains reasoning-heavy but the architectural boundary is already settled:

- difficult debugging;
- non-trivial refactoring;
- multi-module comprehension;
- lifecycle or concurrency reasoning;
- complex state handling;
- compatibility-sensitive implementation;
- localized design judgment.

Keep product decisions, external contract choices, canonical data-model decisions, cross-owner architecture, migration strategy, and significant security-boundary decisions at the root.

### `reviewer` — challenge

Use for independent review after substantial implementation or whenever defect cost justifies a fresh inspection.

Give the reviewer:

- objective;
- acceptance criteria;
- applicable constraints and contracts;
- resulting diff or implementation;
- relevant surrounding code and tests.

Preserve review independence. Prefer the implementation and requirements over the writer's rationale.

Reviewer findings return to the root for triage.

### `validator` — prove gates

Use to execute objective completion gates:

- targeted tests;
- builds;
- type checks;
- lint or static analysis;
- contract tests;
- specification validators;
- focused integration checks.

The validator reports evidence and normally does not repair failures. Failed gates return to the root for disposition.

### `default` — exceptional fallback

Use only when a bounded assignment genuinely spans roles or none of the specialized roles fits.

Do not use `default` merely to avoid decomposing the work.

**Complete when:** every assignment is routed to the narrowest suitable role and root-owned decisions have not leaked into worker authority.

## 4. Execute and integrate

Dispatch independent assignments concurrently when useful. Keep the orchestration tree shallow: the root normally owns all delegation.

Require subagents to return concise evidence appropriate to their role.

For investigation or implementation work, expect:

- result;
- evidence;
- changed files or artifacts, if any;
- validation actually performed;
- assumptions;
- risks;
- blockers.

Do not accept implementation claims solely on trust when the resulting state can reasonably be inspected.

After each dependency boundary or phase, reconcile returned evidence into the root working brief before dispatching dependent work.

**Complete when:** all required implementation assignments have returned, their outputs are mutually coherent, and unresolved decisions or blockers are visible at the root.

## 5. Review substantial changes

Use a fresh `reviewer` when independent inspection materially reduces risk.

The root classifies each finding as:

- **blocking and in scope**;
- **valid and in scope but non-blocking**;
- **valid but out of scope**;
- **unsupported**;
- **optional improvement**.

Assign only actionable findings back to `worker` or `deep-worker`.

After meaningful corrections, re-review the affected behavior when the original finding depended on code that changed.

Avoid indefinite writer-reviewer loops. Repeated disagreement or redesign pressure returns to the root as a decision problem.

**Complete when:** every material review finding has a root disposition and every blocking in-scope finding is resolved or explicitly surfaced as a blocker.

## 6. Validate the resulting state

Send the settled implementation to `validator` with the narrowest credible gate set required by the changed behavior and repository guidance.

Treat validation as evidence, not implementation.

If a gate fails:

1. capture the failing check;
2. distinguish implementation failure from environment or infrastructure failure when evidence permits;
3. return the failure to the root;
4. assign corrective implementation to `worker` or `deep-worker` when appropriate;
5. rerun the affected gate after correction.

Expand validation only when changed boundaries, repository instructions, or observed failures justify it.

**Complete when:** required gates have passed, or every unexecuted/failed gate is explicitly accounted for as a blocker or residual risk.

## 7. Reconcile non-code obligations

Before final acceptance, inspect whether the implementation requires updates to:

- owner-local specifications;
- API or schema documentation;
- architecture or service documentation;
- migration notes;
- playbooks;
- changelog;
- tests representing external contracts.

Delegate mechanical updates to `worker` when useful. Keep contract or architectural decisions at the root.

**Complete when:** every required non-code obligation is updated or explicitly identified as incomplete.

## 8. Prepare final integration

Inspect the final diff and work state as one system.

Check that:

- acceptance criteria are addressed;
- worker outputs agree on contracts and ownership;
- blocking review findings are resolved;
- required validation actually ran;
- required docs/spec/changelog work is present;
- unrelated existing changes are preserved;
- no subagent assumption silently became an architectural decision.

Commit preparation may be delegated as bounded inspection work, but commit, push, history rewrite, merge, deployment, or other external mutations require the authority applicable to the current user request and environment.

**Complete when:** the root can explain the resulting change, its validation evidence, and any remaining blockers or risks without relying on unresolved subagent claims.

## Escalation

Escalate by changing the task conditions, not by blind retries.

Default path:

`worker` → better context or narrower task → `deep-worker` → root decision

Examples:

- Missing context: improve the task packet.
- Oversized task: split it.
- Difficult implementation inside settled boundaries: use `deep-worker`.
- Competing contracts or architectures: return to root.
- Validation failure: root routes a focused correction.
- Reviewer concern: root triages before assigning work.

## Agent economy

Use the minimum fan-out that creates real value.

Prefer a few bounded assignments over many tiny ones. Spend parallelism on independent progress and independent verification, not on duplicated context discovery or competing edits.

The role is a semantic contract, not a permanent model choice. Route by task shape even if the models assigned to these roles change later.
