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

`README.md` is the human-facing source of truth. `docs/recommendations.md` is the policy source for the audit skill. `scripts/codex_harness.py` is the executable source of truth for file copy, backup, sync, and rollback behavior. The install skill is the source of truth for the human-approved config and plugin reconciliation; the sync skill owns manifest updates.

Repository-only harness maintenance skills live under `.agents/skills/`; do not move them into the distributable `skills/` tree.

## Changelog maintenance

Maintain the root `CHANGELOG.md` using Keep a Changelog 1.1.0 and Semantic
Versioning conventions.

- Keep `## [Unreleased]` first until a release is tagged.
- Group notable changes under `Added`, `Changed`, `Deprecated`, `Removed`,
  `Fixed`, and `Security`; omit empty sections.
- Use ISO 8601 dates (`YYYY-MM-DD`) for release headings and reverse
  chronological order.
- Write human-facing summaries. Do not paste raw `git log` output or list
  noise-level commits.
- Record breaking changes, deprecations, removals, and security fixes clearly.
- Before committing notable work, update `Unreleased` from `git log`,
  `git status --short`, `git diff HEAD`, and intended untracked files; include
  staged and unstaged changes.
- At release time, move `Unreleased` entries into a new SemVer heading, add
  the release date, and update comparison links when tags exist.
