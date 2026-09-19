# Codex Harness

This repository distributes a portable, experimental Codex configuration.

When asked to install it:

1. Read `README.md`.
2. Run the platform wrapper or `python scripts/codex_harness.py status`.
3. Create the ignored local rollback snapshot with `backup` before `install`.
4. Use `--yes` only after showing the target paths and backup ID.
5. Validate the install with `status`; report the backup ID.

When asked to roll back, use `list-backups`, choose the requested snapshot, then run `rollback` and report the restored paths.

When asked to sync the local setup into this repository, run `sync --dry-run`, review the diff for machine-specific values, then run `sync --yes` and validate with `status`.

Never copy credentials, session databases, chat history, caches, worktrees, or runtime binaries. Do not install plugins by copying Codex's versioned cache; use `plugins/manifest.json` and the plugin's official install path.

`README.md` is the human-facing source of truth. `scripts/codex_harness.py` is the executable source of truth for file copy, backup, sync, and rollback behavior. The install skill is the source of truth for the human-approved config and plugin reconciliation; the sync skill owns manifest updates.

Repository-only harness maintenance skills live under `.agents/skills/`; do not move them into the distributable `skills/` tree.
