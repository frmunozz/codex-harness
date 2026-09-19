---
name: codex-harness-backup
description: Create a new configuration-only backup of the current local Codex setup.
disable-model-invocation: true
---

# Back Up Codex Harness

Use the repository root as the working directory. Use the available Python command on the machine (`python`, `python3`, or `py -3`) as `PYTHON`.

1. Run `$PYTHON scripts/codex_harness.py status` and confirm the target roots.
2. Run `$PYTHON scripts/codex_harness.py backup`.
3. Report the backup ID and path. Remind the user that credentials, session databases, caches, worktrees, and runtime binaries are outside the backup scope.

Done means the command succeeds and the backup ID is recorded.
