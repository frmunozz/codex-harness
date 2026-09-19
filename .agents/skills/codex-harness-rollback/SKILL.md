---
name: codex-harness-rollback
description: Restore the local Codex setup from a user-selected harness backup.
disable-model-invocation: true
---

# Roll Back Codex Harness

Use the repository root as the working directory. Use the available Python command on the machine (`python`, `python3`, or `py -3`) as `PYTHON`.

1. Run `$PYTHON scripts/codex_harness.py status`.
2. Run `$PYTHON scripts/codex_harness.py list-backups`.
3. Present the available backup IDs and ask the user to choose one. A backup ID is required; never infer or silently choose one.
4. Run `$PYTHON scripts/codex_harness.py rollback <selected-id> --dry-run`, show every restore/remove target, then get confirmation.
5. Run `$PYTHON scripts/codex_harness.py rollback <selected-id> --yes`.
6. Run `$PYTHON scripts/codex_harness.py status` and report the restored-entry count, including whether `config.toml` was restored.

Rollback restores the selected manifest exactly: files and directory trees that existed are restored; paths marked absent are removed. This includes `.agents/skills/`, `.codex/skills/`, and `.agents/.skill-lock.json` when the backup contains them. It does not merge config, install plugins, or touch paths outside the selected backup.

Done means the selected backup was restored and status succeeds.
