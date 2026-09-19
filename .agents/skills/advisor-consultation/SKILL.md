---
name: advisor-consultation
description: Consult the high-capability advisor when targeted fact finding has reduced a difficult problem to consequential unresolved judgment. Use for material architecture, contract, data, migration, compatibility, security, reversibility, or high-rework decisions and targeted critical audits; not for ordinary uncertainty, implementation difficulty, or facts repository exploration can resolve.
---

# Advisor Consultation

Use this reusable skill when targeted fact finding has reduced a problem to consequential unresolved judgment.

## Advisor trigger

Advisor use requires both gates.

### Consequence gate

At least one must apply:

- material external/API/data contract consequence;
- canonical data or app/package/service ownership consequence;
- schema, migration, compatibility, or production data-integrity consequence;
- authentication, authorization, privacy, trust, or other security-boundary consequence;
- impact to a core invariant relied upon across components;
- broad blast radius with substantial rework if the recommendation is wrong;
- architectural choice that is difficult or expensive to reverse.

Task difficulty alone does not satisfy this gate.

### Judgment gate

Resolve cheap factual uncertainty first.

Use repository evidence or `explorer` when material facts are missing.

The gate passes only if, after targeted fact finding, repository authority still does not mechanically determine the answer and one or more remains:

- multiple materially different approaches are plausible;
- authoritative sources conflict or leave important policy unspecified;
- the issue requires a consequential tradeoff rather than a factual lookup;
- root confidence remains materially low after investigation;
- a review or implementation finding exposes architecture/contract ambiguity;
- repeated attempts suggest the underlying decision or approach may be wrong;
- the proposed approach intentionally departs from an established repository pattern;
- the decision is difficult to reverse and preservation of relevant invariants has not been established.

If authoritative repository/specification evidence already determines the answer, follow it without advisor consultation.

## Advisor context boundary

The parent/root owns fact finding and context assembly. The advisor receives a compressed packet as its complete context boundary and performs reasoning only.

The advisor is not an explorer. Do not send broad repository context or ask the advisor to reconstruct missing facts.

If the packet is insufficient, the advisor returns exactly one specific material fact or clarification required from the parent/root. The parent/root supplies it; the advisor does not obtain it.

## Advisor context packet

Before invoking `advisor`, reduce the problem into:

```markdown
### Decision
Exactly one decision that must be made.

### Why this requires advice
State which consequence applies and what judgment remains unresolved.

### Desired outcome
The behavior, invariant, or system property that must be achieved or preserved.

### Confirmed facts
Only evidence-backed facts that materially affect the decision.

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

### Candidate approaches
Only serious remaining alternatives.
For each, summarize the meaningful consequence or tradeoff in one or two sentences.
Omit for a targeted audit when appropriate.

### Material unknowns
Only unknowns that could change the recommendation and cannot cheaply be resolved before consultation.

### Exact question
Ask one concrete decision question.
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

Support two modes:

### Decision mode

Use when choosing among consequential alternatives.

Present viable alternatives neutrally. Avoid unnecessarily anchoring the advisor with the root's preferred answer.

### Audit mode

Use when testing one consequential proposal, decision, or implementation against a specific invariant or high-risk concern.

Provide only:

- the invariant or risk being audited;
- relevant authoritative evidence;
- the concise proposed decision or change;
- the smallest relevant code or diff context.

## Advisor response contract

Expect:

```text
Recommendation:
One preferred decision, or the exact missing material fact required.

Reasoning:
The 2-4 considerations that actually determine the recommendation.

Primary risk:
The most important downside or failure mode.

Confidence:
high | medium | low

Decision-changing condition:
The fact or condition that would materially change the recommendation.
```

## Follow-up limit

Prefer one advisor invocation per decision.

If the advisor cannot reliably decide because one specific material fact is missing:

1. resolve that fact through repository evidence or `explorer`;
2. allow one focused advisor follow-up.

Do not respond to a request for more information by dumping broad context.

After one follow-up, unresolved ambiguity returns to the root/user rather than creating an open-ended advisor loop.

## Authority

The advisor provides high-value evidence and recommendations.

The root retains final decision authority.
