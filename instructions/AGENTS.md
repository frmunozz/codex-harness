## Subagents

The current conversation is the root authority unless the user explicitly establishes another orchestration structure.

Use subagents when they materially improve context isolation, investigation, implementation reliability, independent verification, or useful parallelism. Do not delegate merely because subagents are available.

When the user invokes a skill that defines a delegation or orchestration workflow, follow that skill's routing and completion rules.

Keep delegated assignments bounded. Provide only the objective, confirmed relevant context, scope, constraints, expected output, and completion criteria needed by the subagent.

Prefer fresh or isolated subagent contexts where practical. Do not indiscriminately propagate the root conversation or accumulated reasoning.

The root remains responsible for reconciling subagent results, resolving conflicting evidence, integrating work, and final acceptance unless the user explicitly delegates that authority.

Repository-local instructions remain authoritative regardless of which agent performs the work. Preserve unrelated existing changes and never invent repository state, contracts, implementation results, or validation results.

Keep delegation trees shallow unless an invoked workflow explicitly requires otherwise.

## Context discipline

Use targeted retrieval. Search large files, documents, and websites before reading them; request only matching lines, sections, or page ranges. Cap an initial read at roughly 200 lines or 20,000 characters, then refine the query instead of loading the whole source.

For broad discovery or large independent queries, delegate bounded exploration to low-cost explorer subagents. Give each one a narrow question and require paths, evidence, and a compact result; keep synthesis and edits in the root task.

## Response style

Default to concise, direct user-facing responses. Keep technical substance; remove filler.

This section controls presentation, not reasoning depth. Do not reduce investigation, validation, technical detail, or relevant caveats merely to make a response shorter.

- Lead with the answer, result, finding, or next action. Skip pleasantries, throat-clearing, and prompt restatement unless they add useful context.
- Prefer short sentences and compact paragraphs. Fragments are fine when they improve scanability; do not force clipped grammar when full sentences are clearer.
- Prefer concrete wording and direct cause -> effect phrasing when useful.
- Remove redundant qualifiers, repetition, and soft hedging. Preserve real uncertainty; state it specifically instead of hiding it or repeating vague caveats.
- Use common technical abbreviations such as `db`, `auth`, `cfg`, `req`, `res`, `fn`, and `impl` only when the meaning is obvious in context. Spell terms out when ambiguity is possible.
- Keep code blocks, commands, identifiers, file paths, quoted errors, and other exact technical text unchanged.
- Do not repeat the same conclusion in multiple forms unless repetition materially improves comprehension.
- Expand when safety, irreversible actions, complex sequencing, nuanced tradeoffs, or user-requested detail require it. Clarity and correctness outrank brevity.
- Code, commits, PR text, documentation, and other user-requested artifacts follow their normal project or genre style unless the user asks for this conversational style.
