---
name: codex-harness-rollback
description: Restore the local Codex setup from a user-selected harness backup.
disable-model-invocation: true
---

# Roll Back Codex Harness

Use the repository root as the working directory. Use the available Python command on the machine (`python`, `python3`, or `py -3`) as `PYTHON`.

1. Run `$PYTHON scripts/codex_harness.py status`.
2. Run `$PYTHON scripts/codex_harness.py list-backups`.
3. Present the available backup IDs and ask the user to choose one. Never silently choose `latest`.
4. Run `$PYTHON scripts/codex_harness.py rollback <selected-id> --dry-run`, show the target, then get confirmation.
5. Run `$PYTHON scripts/codex_harness.py rollback <selected-id> --yes`.
6. Run `$PYTHON scripts/codex_harness.py status` and report the restored-file count.

Done means the selected backup was restored and status succeeds.
