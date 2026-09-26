---
name: pr-review-loop
description: Orchestrate independent PR reviews, evidence gathering, Astra triage, bounded fixes, validation, scope checks, and local commits for up to five iterations. Use only when explicitly invoked.
disable-model-invocation: true
---

# PR Review Loop

Use this skill when explicitly asked to run an iterative review of the current pull request. The root is the only orchestrator. Reviewers find issues, explorers gather missing evidence, `review-triage` classifies findings, workers implement approved fixes, and the root integrates and commits each accepted iteration.

## Flow

```text
Freeze PR brief, base, and local ledger
                 │
                 ▼
      ┌──── Independent review wave ────┐
      │ Codex CLI │ Ponytail │ Matt:    │
      │           │          │ Standards│
      │           │          │ Spec     │
      └────────────────┬────────────────┘
                       ▼
             Normalize and deduplicate
                       ▼
       Explorers gather only missing evidence
                       ▼
             Astra review-triage
          address / defer / ignore
                 ┌─────┴─────┐
            no address     address findings
                 │              ▼
                DONE      Build dependency graph
                                ▼
                 Independent fixes? ── yes ──► workers × N
                         │ no                     │
                         ▼                         │
                     worker × 1 ◄─────────────────┘
                         ▼
                Root integrates and validates
                         ▼
                 Fresh Scope/Drift review
                    │ pass      │ drift
                    ▼           └──► narrow/fix, revalidate, re-review
              Root commits locally
               (never push)
                    ▼
             Update ledger; repeat
          at most 5 fix iterations
                    ▼
         one terminal review-only wave
```

## Loop invariants

- Freeze the PR goal, acceptance criteria, non-goals, base commit, and constraints before the first review. That brief remains the scope authority for every iteration.
- Run at most five fix iterations. After the fifth commit, run one terminal review-only wave; do not start a sixth fix iteration. Report any remaining addressable findings as unresolved.
- Review agents do not implement. Explorers gather only evidence needed to assess findings. `review-triage` owns finding dispositions; the root retains final authority.
- Only findings classified `address` may create implementation work. A regression caused by the PR remains addressable even when its repair is outside the original feature scope.
- Workers never commit or push. The root integrates, validates, completes the Scope/Drift gate, and makes one local commit per accepted fix iteration. Never push.
- Use independent workers only when their tasks and write surfaces do not overlap. Use one worker for coupled or linear fixes.
- A failed or timed-out review lane is incomplete, never clean. Do not declare the PR review complete while any required lane remains incomplete.
- Read the ledger before each stage and update it after each reviewer, explorer, triage, worker, validation, drift, or commit handoff.
- Stop when a complete review wave has no findings classified `address`; deferred and ignored findings may remain and must be reported.

## 1. Initialize the review session

1. Read the repository's applicable `AGENTS.md` instructions and inspect `git status`, the current branch, the candidate diff, and recent PR context.
2. Resolve the PR base from the explicit request or the current PR metadata. Record both the stable base commit SHA and its human-readable ref. Do not guess a base branch. If the base or the PR's intended outcome is unclear, ask the user before launching reviewers.
3. Freeze a brief with the original goal, acceptance criteria, non-goals, authoritative issue/spec links or paths, compatibility constraints, and the base commit. Use the PR description and source issue as evidence; do not infer scope from the current implementation alone. If the goal changes during the session, stop and re-baseline only with the user's direction.
4. Record the starting `HEAD` and working-tree state. Treat pre-existing changes as user-owned. Do not overwrite them or include them in a fix commit. If the iteration's changes cannot be separated safely from pre-existing edits, stop before committing and report the conflict.
5. Keep the ledger outside the worktree so it cannot enter the PR diff. Resolve its root with `git rev-parse --git-path codex-review-loop`, then use a stable filename derived from the sanitized branch name and frozen base SHA. Create the directory if needed. If a matching ledger exists, read it and resume only when its PR brief and base match; otherwise start a distinct session file.
6. Write the frozen brief, base, branch, starting `HEAD`, initial `git status`, and session key to the ledger before dispatching work.

The ledger is local operational state, not a source of truth for code or requirements. Never put credentials, tokens, or unrelated private data in it.

Keep this structure current as stages complete:

```markdown
# PR Review Loop

## Frozen brief
- Goal, acceptance criteria, non-goals, base ref and SHA, branch
- Starting HEAD and initial working-tree state

## Finding index
| ID | Fingerprint | Source(s) | Location | Disposition | Status | Commit |

## Round N
### Review lanes
- Result, completion status, and any failure for each lane
### Findings and evidence
- Original reports, correlated IDs, explorer evidence
### Triage
- Disposition, rationale, confidence, implementation constraint
### Implementation
- Worker assignments and results, changed paths, root integration notes
### Validation and Scope/Drift
- Commands and outcomes, reviewer verdict, corrections made
### Commit
- SHA, included finding IDs, final worktree status
```

## 2. Run the independent review wave

Review the same frozen `base...HEAD` range in each lane. If local changes are part of the candidate PR, include them explicitly in the review context and preserve their pre-existing status in the ledger. Do not silently omit uncommitted or untracked changes.

Run four independent outputs:

1. **Native Codex review:** from the root, run `codex exec review --base <frozen-base-ref-or-sha>` with a 10-minute wall-clock timeout. If staged, unstaged, or untracked candidate changes exist, also run `codex exec review --uncommitted` with the same timeout and include that result in the Codex lane. These are separate invocations; do not combine `--base` and `--uncommitted`. Do not ask a subagent to invoke the App's `/review` command. If the CLI is missing, fails, hangs, or returns an incomplete result, record the lane as incomplete; do not interpret empty output as approval.
2. **Ponytail review:** use the installed Ponytail review skill as one independent reviewer. Keep its focus on unnecessary complexity, abstractions, dependencies, and code that can be removed. If the skill is unavailable, record the lane as incomplete rather than substituting another reviewer.
3. **Matt Pocock Standards review.**
4. **Matt Pocock Spec review.**

For the Matt lanes, read the installed `code-review` skill and follow its requirements. Keep the Standards and Spec passes as separate reviewer assignments using the configured read-only `reviewer` profile. Flatten them at the root: do not delegate to a child that may launch its own nested reviewers. If the skill or a reviewer lane is unavailable, record it as incomplete.

Give every reviewer the frozen brief, exact review range, and only the surrounding context needed for its axis. Require actionable findings with file and line/hunk, concrete evidence, credible impact, and uncertainty clearly labeled. Reviewers must not edit files or implement fixes. Record each result in the ledger as it returns.

### Normalize and correlate findings

Assign stable IDs such as `R1-F1` (round and finding number). Preserve each reviewer's original finding text and source. Record path, line/hunk, claim, evidence, impact, confidence, and a normalized fingerprint. Correlate duplicates while retaining all source IDs; do not merge findings whose root causes or fixes differ.

Compare new results with the ledger. Mark findings as new, repeated, already fixed, deferred again, or materially changed. Re-triage a repeated finding when the relevant code or evidence has changed. Never count an unavailable reviewer as having found zero issues.

If any required lane is incomplete, retry that lane once after checking its specific failure. Continue triage and safe fixes for findings already supported by complete lanes, but do not declare the review clean. If a lane remains incomplete after the retry, end with an incomplete-review report after handling any approved work that can safely proceed.

## 3. Gather only missing evidence

For each finding, first check whether the reviewer handoff already establishes the relevant facts. Spawn a fresh `explorer` only when missing repository evidence could change whether the finding is valid, in scope, or safe to fix. Group related findings for one explorer when they share an investigation. Ask for the smallest decisive evidence and prohibit edits, fixes, or broad review.

Record the explorer's evidence in the ledger before triage. If evidence remains insufficient, leave the uncertainty explicit and do not ask `review-triage` to guess.

## 4. Triage findings with Astra

Send `review-triage` the frozen PR brief, normalized findings, reviewer provenance, and explorer evidence. Batch findings when the packet remains readable; split only when independent batches materially improve clarity. Read the ledger before the consultation and record its result immediately after.

For every canonical finding, capture:

```text
Finding: <canonical ID and correlated source IDs>
Disposition: address | defer | ignore
Scope impact: in-scope | regression-caused | out-of-scope
Priority: blocking | normal
Confidence: high | medium | low
Reason: <evidence-based rationale>
Implementation constraint: <constraint or none>
```

If the agent requests material evidence, return to the evidence stage with an explorer, then continue the same triage consultation if supported; otherwise start a fresh consultation with the completed packet. The root makes the final decision and records any disagreement with the triage recommendation.

When no findings are classified `address`, finish if every review lane completed. If lanes remain incomplete, follow the incomplete-lane rule and report the review as incomplete.

## 5. Implement approved findings

Build a dependency graph for all `address` findings. Assign independent, non-overlapping groups to workers in parallel; assign coupled or sequential fixes to one worker. Each packet includes the finding IDs, evidence, exact behavior to change, implementation constraints, allowed write surface, and completion criteria.

Workers do not decide scope, reclassify findings, stage changes, commit, or push. If implementation reveals a material new decision or scope change, return it to the root. After workers finish, read the ledger, inspect every changed file and diff, reconcile overlapping results, and update the ledger with actual changes and assumptions.

## 6. Validate and run the Scope/Drift gate

Run the targeted checks needed to verify the approved fixes. Record the exact commands and outcomes. A failed check returns to implementation or an explicit root disposition; do not commit an unverified fix.

After validation and before commit, use a fresh read-only `reviewer` for a Scope/Drift pass. Supply:

- the frozen PR brief and non-goals;
- iteration-start `HEAD` and the iteration-end diff;
- the findings approved for `address`;
- validation results.

Ask whether every change is necessary to resolve approved findings or achieve the frozen goal. Require this response:

```text
Verdict: on-track | drift detected | uncertain
Expected changes: <findings and goal-related changes>
Possible drift: <specific path/hunk and rationale, or none>
Unapproved scope expansion: <specific changes, or none>
Recommendation: accept iteration | narrow/fix | investigate
```

If drift is detected, narrow or revert only the unrelated changes, rerun affected validation, and repeat the gate within the same fix iteration. If the verdict is uncertain, gather the smallest missing evidence or narrow the change; do not treat uncertainty as a pass. Record the final gate result in the ledger.

## 7. Commit locally and continue

After validation and a passing Scope/Drift gate, the root makes one logical local commit for the iteration. Use the `git-commit` skill for message and safe staging guidance when available. Stage only this iteration's fix hunks; never use `git add -A` when pre-existing or unrelated changes exist. Confirm the staged diff contains only approved fixes before committing. If safe separation is impossible, stop before commit and report why. Never push.

Record the commit SHA, included finding IDs, validation results, and final worktree state in the ledger. Then read the ledger and begin the next review wave against the same frozen base.

After five fix commits, run one terminal review-only wave. Triage its findings but do not implement a sixth iteration. Report remaining `address` findings as unresolved. A complete terminal wave with no `address` findings closes the loop.

## 8. Final report

Summarize:

- frozen PR goal, base, and number of review/fix iterations;
- completed, incomplete, or timed-out review lanes;
- each finding's disposition, evidence gathered, and implementation status;
- fix commit SHAs and validation actually run;
- final Scope/Drift verdicts;
- deferred and ignored findings with concise reasons;
- unresolved addressable findings or blockers;
- the ledger path.

Never describe an incomplete review wave as clean or approved.
