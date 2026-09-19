---
name: codex-harness-sync
description: Sync the current local Codex setup back into this repository for maintenance.
disable-model-invocation: true
---

# Sync Codex Harness

Use the repository root as the working directory. Use the available Python command on the machine (`python`, `python3`, or `py -3`) as `PYTHON`.

1. Run `$PYTHON scripts/codex_harness.py status` to identify `CODEX_HOME` and `AGENTS_HOME`.
2. Run `$PYTHON scripts/codex_harness.py sync --dry-run`. Explain that the command copies managed local files into the repository but intentionally excludes `config.toml`; flag machine-specific paths, trust entries, commands, and runtime values for review.
3. Get confirmation, then run `$PYTHON scripts/codex_harness.py sync --yes`.
4. Run `git diff --check`, inspect `git diff --stat`, and run `$PYTHON scripts/codex_harness.py status`.
5. Report changed paths and any values the user should remove before committing. If the portable config baseline needs updating, edit `config/config.toml.template` deliberately; never copy a user's local `config.toml` into it. Never copy credentials, session databases, chat history, caches, worktrees, or runtime binaries.

Done means sync completed, diff checks pass, and the repository diff was reviewed for local-only values.
