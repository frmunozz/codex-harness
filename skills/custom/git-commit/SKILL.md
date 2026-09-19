---
name: git-commit
description: Plan and execute git commits with adaptive grouping for small and very large diffs. Use when the user asks to commit changes, split work into logical commits, or improve commit quality. Analyze git diff plus repository docs, assess impact, group files into coherent commits, and generate detailed Conventional Commit messages. If more than 10 commits are proposed, request user approval or a maximum count, then regroup and regenerate messages to match the approved limit.
---

# Git Commit

Produce reviewable, reversible commit history that reflects logical change intent.

## Workflow

1. Inspect current git state.
2. Read repository guidance and impacted docs.
3. Analyze code impact and dependencies.
4. Build logical commit groups.
5. Enforce commit-count gate.
6. Generate detailed commit messages.
7. Stage and commit safely.

## 1) Inspect Git State

Run:

- `git status --short`
- `git diff --staged --name-status`
- `git diff --name-status`
- `git diff --staged --stat`
- `git diff --stat`
- `git ls-files --others --exclude-standard`

Prefer staged diff when staged files exist. Use working-tree diff when nothing is staged. Include untracked files in grouping decisions.

## 2) Read Repository Context

Before proposing commit groups, read documentation that defines expected behavior:

- Root `AGENTS.md`
- Nearest nested `AGENTS.md` files for changed areas
- `README.md` and service docs relevant to touched paths
- Spec/contract docs when API/schema/interfaces changed

Do not scan the entire docs tree when unnecessary. Read only files needed to understand impact.

## 3) Analyze Impact

Classify every changed file:

- Behavioral code
- Contracts/schemas/APIs
- Tests
- Docs
- Build/CI/infra
- Formatting/generated artifacts

Identify:

- Runtime impact areas (services, shared packages, infra, tooling)
- Coupled changes that must stay together (code + tests + migrations)
- Potential breaking changes
- Risk level (low/medium/high)

For very large diffs, reduce noise:

- Cluster by top-level path first.
- Use `git diff --numstat` and `git diff --dirstat=files,0` to prioritize hotspots.
- Read full patch only for representative or high-impact files in each cluster.

## 4) Build Commit Groups

Create one logical intent per group. Keep groups independently understandable.

Use these grouping rules:

- Keep feature code and its tests together.
- Keep migrations with code that depends on them.
- Keep broad formatting/chore changes separate from behavior changes.
- Keep docs separate unless docs are required to understand the code change.
- Avoid mixing unrelated domains in one commit.

Scale policy:

- Small change set (1-15 files): prefer fine-grained logical commits.
- Medium (16-80 files): group by feature/module plus change intent.
- Large (81+ files): group by domain first, then split by feature.

## 5) Enforce Commit-Count Gate

Let `N` be the number of candidate commit groups.

- If `N <= 10`, continue.
- If `N > 10`, pause and ask for confirmation:
  - "I prepared `N` commit groups. Approve `N` commits, or provide a maximum number of commits to use."

If the user provides a maximum `M`:

- Regroup to produce at most `M` commits.
- Preserve mandatory couplings (code/tests/migrations/contracts).
- Merge nearest groups by shared module, scope, and risk profile.
- Regenerate all commit messages after regrouping.
- Present the updated grouping and wait for approval.

Commit execution gate:

- If `N <= 10` and the user asked to execute commits, continue without an extra confirmation prompt.
- If `N <= 10` and the user asked only to prepare/draft commits, do not run `git commit`.
- If `N > 10`, always require approval (or a maximum `M`) before any commit execution.

## 6) Generate Detailed Commit Messages

Use Conventional Commits:

```
<type>[optional scope]: <subject under 72 chars>

<body with key changes and rationale>

[optional footer(s)]
```

Message rules:

- Use imperative mood in subject.
- Keep subject concise and specific.
- Use body to capture what changed, why, and impact.
- Add `BREAKING CHANGE:` footer when behavior/contracts break compatibility.
- Add issue references when available (`Fixes #123`, `Refs #456`).

For each group, output:

1. Group label and rationale
2. Files in the group
3. Commit type/scope decision
4. Full commit message (subject/body/footer)

## 7) Stage and Commit Safely

When commit execution is allowed by Section 5, commit each group in sequence:

1. Stage only files for the current group.
2. Verify staged content matches the planned group (`git diff --staged --name-only`).
3. Run `git commit` with the generated message.
4. Repeat for remaining groups.

Safety rules:

- Never commit secrets (`.env`, keys, credentials, tokens).
- Never use destructive git commands unless explicitly requested.
- Never use `--no-verify` unless explicitly requested.
- Never amend commits unless explicitly requested.
- If hooks fail, report failure and propose fixes before retrying.

## Output Contract

When asked to "prepare commits," produce:

1. A short impact summary
2. Proposed grouping count and labels
3. Full commit messages for each group
4. No `git commit` execution

When asked to execute commits:

1. Show the same summary/grouping/messages first
2. Execute commits directly when `N <= 10`
3. Require approval/regrouping only when `N > 10`
