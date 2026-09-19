## Subagents

The current conversation is the root authority unless the user explicitly establishes another orchestration structure.

Use subagents when they materially improve context isolation, investigation, implementation reliability, independent verification, or useful parallelism. Do not delegate merely because subagents are available.

When the user invokes a skill that defines a delegation or orchestration workflow, follow that skill's routing and completion rules.

Keep delegated assignments bounded. Provide only the objective, confirmed relevant context, scope, constraints, expected output, and completion criteria needed by the subagent.

Prefer fresh or isolated subagent contexts where practical. Do not indiscriminately propagate the root conversation or accumulated reasoning.

The root remains responsible for reconciling subagent results, resolving conflicting evidence, integrating work, and final acceptance unless the user explicitly delegates that authority.

Repository-local instructions remain authoritative regardless of which agent performs the work. Preserve unrelated existing changes and never invent repository state, contracts, implementation results, or validation results.

Keep delegation trees shallow unless an invoked workflow explicitly requires otherwise.
