---
name: recent-work-summary
description: Build a copy-ready business summary of work completed in the
  last N days by analyzing recent git commits, diff stats, pull requests,
  and GitHub issues for the current repository. Use when the user asks for a
  weekly status update, business-facing summary, bilingual English/Spanish
  report, retrospective of recent work, or a shareable overview of recent
  changes and pending items.
---

# Recent Work Summary

## Overview

Use this skill to turn recent repository activity into a business-facing
summary that is specific enough to share with stakeholders. The bundled
script gathers commit history, line counts, impacted paths, PR context, issue
context, and likely pending items so the final narrative is grounded in
actual repository evidence instead of guesswork.

## Inputs

- `repo`: repository path to inspect; default to the current working tree.
- `days`: reporting window; default to `7` unless the user asks for another
  value.
- `author`: optional git author override when the work should be filtered to a
  specific name or email instead of the configured local user.
- `github-user`: optional GitHub login override when `gh auth status` points
  to a different account than the one that authored the work.

## Workflow

1. Resolve the reporting window.
   - If the user gives a number of days, use it directly.
   - Otherwise default to `7`.
2. Run the collector script.
   - Command:
     ```powershell
     python "<skill-path>\scripts\collect_recent_work.py" --repo "." --days 7
     ```
   - Add `--author "name-or-email"` if git identity matching needs to be
     tightened.
   - Add `--github-user "login"` if GitHub activity belongs to a different
     account.
3. Read the JSON output.
   - Treat `git` as the ground truth for commits, changed files, and line
     counts.
   - Treat `github` as supporting context for PR titles, issue scope, and open
     follow-up work.
   - If `github.available` is `false`, keep the summary git-based and say that
     GitHub context was unavailable.
4. Draft the business summary using
   [output-format.md](./references/output-format.md).
   - Write the English section first.
   - Mirror the same facts in Spanish; do not introduce facts in one language
     that do not appear in the other.
5. Verify pending work.
   - Use the `pending` array first.
   - Cross-check open PRs, open issues, draft PRs, and dirty local workspace
     state before claiming that nothing is pending.

## Output Rules

- Keep the summary copy-ready in Markdown.
- Stay business-oriented, but keep concrete technical evidence:
  commit count, files changed, insertions, deletions, and major impacted
  areas.
- Mention affected features or subsystems using commit subjects, PR titles,
  issue titles, and dominant path areas.
- Mention pending items explicitly. If none are found, say so explicitly.
- Do not invent feature impact that is not supported by the collected data.
- If the user asks for a shorter version, condense the narrative but keep both
  languages and the change-volume data.

## Resources

### scripts/collect_recent_work.py

Collect structured context for a recent-work summary.

Examples:

```powershell
python "<skill-path>\scripts\collect_recent_work.py" --repo "." --days 5
python "<skill-path>\scripts\collect_recent_work.py" --repo "." --days 14 --author "you@example.com"
python "<skill-path>\scripts\collect_recent_work.py" --repo "." --days 7 --github-user "your-github-user"
```

### references/output-format.md

Defines the required sections and writing rules for the bilingual business
summary.
