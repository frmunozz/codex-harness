---
name: advisor-consultation
description: Consult the high-capability advisor for a high-impact engineering checkpoint when targeted fact finding leaves consequential judgment or when an independent plan, approach, implementation, or fix validation would materially reduce risk. Not for routine changes, ordinary uncertainty, implementation difficulty alone, or facts repository exploration can resolve.
---

# Advisor Consultation

Use this reusable skill for a high-impact engineering checkpoint where stronger independent reasoning can materially improve a decision or reduce execution risk.

## Advisor trigger

Advisor use requires the impact gate and at least one advice reason:

`advisor = impact gate AND (judgment reason OR validation reason)`

### Impact gate

At least one must apply:

- material external/API/data contract consequence;
- canonical data or app/package/service ownership consequence;
- schema, migration, compatibility, or production data-integrity consequence;
- authentication, authorization, privacy, trust, or other security-boundary consequence;
- impact to a core invariant relied upon across components;
- substantial new user-facing feature or multi-module behavior with material regression risk;
- high-impact production bug/fix or a change to a core/shared module;
- broad blast radius with substantial rework if the recommendation is wrong;
- architectural choice that is difficult or expensive to reverse.

Task size, implementation difficulty, or the mere presence of a new feature does not satisfy this gate by itself.

### Judgment reason

Resolve cheap factual uncertainty first. Use repository evidence or `explorer` when material facts are missing.

The judgment reason applies when, after targeted fact finding, repository authority still does not mechanically determine the answer and one or more remains:

- multiple materially different approaches are plausible;
- authoritative sources conflict or leave important policy unspecified;
- the issue requires a consequential tradeoff rather than a factual lookup;
- root confidence remains materially low after investigation;
- a review or implementation finding exposes architecture/contract ambiguity;
- repeated attempts suggest the underlying decision or approach may be wrong;
- the proposed approach intentionally departs from an established repository pattern;
- the decision is difficult to reverse and preservation of relevant invariants has not been established.

If authoritative repository/specification evidence already determines the answer, do not use the judgment reason merely to obtain confirmation.

### Validation reason

The validation reason applies when the root already has a plausible plan, approach, implementation, or fix, but an independent higher-capability challenge could materially reduce risk before proceeding or accepting the work.

Typical checkpoints include:

- validating the sequence or rollback characteristics of a high-impact implementation plan before execution;
- challenging the implementation approach for a substantial new feature or multi-module refactor;
- auditing a consequential implementation against a core invariant, compatibility requirement, or security boundary;
- validating a critical or cross-cutting bug fix against its suspected root cause and regression risk;
- checking a risky migration, ownership change, or shared-module modification for hidden coupling.

Do not create an advisor checkpoint for routine localized work where independent review is unlikely to change the plan or materially reduce risk.

## Consultation lifecycle

Each advisor is consultation-scoped.

- Spawn a fresh `advisor` for one coherent checkpoint.
- Do not reuse an advisor from an earlier completed consultation, even when the later question belongs to the same workstream.
- Keep the same advisor alive while that consultation is active, including targeted clarification turns.
- After the advisor returns final advice and the root records or integrates it, close the advisor immediately.
- A later distinct checkpoint starts a new advisor consultation.

This keeps advisor context current without making the root track long-lived advisor threads.

## Advisor context boundary

The parent/root owns fact finding and context assembly. The advisor receives a compressed initial packet and performs reasoning only.

The advisor is not an explorer. Do not send broad repository context or ask the advisor to reconstruct missing facts.

During the active consultation, the advisor may ask the parent/root targeted clarification questions when an answer could materially change the recommendation. The root answers from established evidence or uses `explorer` to obtain a missing repository fact, then returns only the relevant answer to the same advisor.

The advisor does not inspect the repository or obtain missing facts itself.

## Advisor context packet

Before invoking `advisor`, reduce the problem into:

```markdown
### Consultation type
Decision | Plan check | Approach check | Audit

### Subject
Exactly one decision, plan, approach, implementation, or fix to evaluate.

### Why this requires advice
State which impact condition applies and whether the need is unresolved judgment, independent validation, or both.

### Desired outcome
The behavior, invariant, or system property that must be achieved or preserved.

### Confirmed facts
Only evidence-backed facts that materially affect the consultation.

### Constraints
Only constraints that eliminate or materially affect choices:
- authoritative specifications;
- ownership boundaries;
- compatibility requirements;
- external contracts;
- data-integrity requirements;
- migration constraints;
- security constraints;
- explicit scope limitations.

### Options or proposal
For decision mode, include only serious remaining alternatives and their meaningful tradeoffs.
For plan, approach, or audit modes, include the concise proposal being validated.

### Material unknowns
Only unknowns that could change the recommendation and cannot cheaply be resolved before consultation.

### Exact question
Ask one concrete question.
For audit mode, state one invariant or risk to falsify.
```

Do not send:

- the full root conversation;
- accumulated chain of reasoning;
- raw exploration logs;
- broad repository dumps;
- complete branch diffs when a smaller relevant diff is sufficient;
- abandoned alternatives;
- unrelated implementation history.

## Modes

Support four modes.

### Decision

Use when choosing among consequential alternatives.

Present viable alternatives neutrally. Avoid unnecessarily anchoring the advisor with the root's preferred answer.

### Plan check

Use before execution when a high-impact plan's sequencing, dependencies, rollback behavior, or omitted steps deserve independent challenge.

### Approach check

Use when the intended outcome is established but the proposed technical approach for high-impact work deserves independent challenge before or during implementation.

### Audit

Use when testing a consequential implementation or fix against a specific invariant or high-risk concern.

Provide only the relevant authoritative evidence, concise proposal/change, and smallest code or diff context needed for that audit.

## Clarification dialogue

The advisor may doubt the packet and ask for more information before giving final advice.

A clarification question must satisfy this test: knowing the answer could plausibly change the recommendation, confidence, or primary risk.

When clarification is requested:

1. keep the same advisor consultation open;
2. answer directly from confirmed evidence when the root already knows the fact;
3. use a fresh `explorer` when repository investigation is needed;
4. return only the relevant fact or clarification to the advisor;
5. let the advisor reassess whether another material clarification is required.

Prefer one focused clarification at a time. Combine only tightly related questions that can be answered from the same evidence.

Normally allow at most three clarification rounds for one consultation. If material uncertainty remains after that, ask the advisor for its final best-effort disposition rather than continuing indefinitely.

Do not spawn another advisor to answer questions from the current advisor, and do not dump broad extra context in response to a clarification request.

## Advisor response contract

Before final advice, the advisor may return:

```text
Clarification needed:
The smallest specific question or fact request required from the parent.

Why it matters:
How the answer could materially change the recommendation.
```

Final advice must return:

```text
Recommendation:
One preferred decision. If material uncertainty still prevents a responsible recommendation, say "Defer - insufficient evidence" and identify the blocking uncertainty.

Reasoning:
The 2-4 considerations that actually determine the recommendation.

Primary risk:
The most important downside or failure mode.

Confidence:
high | medium | low

Decision-changing condition:
The fact or condition that would materially change the recommendation.
```

After receiving the final response, the root records or integrates the advice and closes the advisor.

## Authority

The advisor provides high-value evidence and recommendations.

The root retains final decision authority.
