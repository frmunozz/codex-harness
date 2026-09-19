# Codex Harness

Portable, experimental Codex user configuration for Windows, macOS, and Linux.

Contents:

- `skills/` — distributable shared skills copied to the user skill directory.
- `.agents/skills/` — repository-only maintenance skills; never installed globally.
- `agents/` — reusable subagent presets.
- `instructions/` — global `AGENTS.md` guidance.
- `hooks/` — cross-platform hook scripts and activation templates.
- `config/config.toml.template` — safe portable configuration baseline for the install skill.
- `plugins/manifest.json` — desired plugin inventory and source notes; install/sync skills reconcile it with live plugin state.
- `scripts/` — backup, install, status, sync, and rollback tooling.

## Fast install

Run from the repository root.

Windows PowerShell:

```powershell
.\scripts\install.ps1 --yes
```

macOS/Linux:

```bash
bash scripts/install.sh --yes
```

Equivalent direct command:

```text
python scripts/codex_harness.py install --yes
```

Use `python3` where that is the local command.

The installer backs up existing managed files first. It also backs up `config.toml` for rollback, but does not replace it; the install skill reviews and merges the config baseline after human approval. Backups go to `backup/<timestamp>/`; `.gitignore` prevents them from entering Git.

## Preview and backup

```text
python scripts/codex_harness.py status
python scripts/codex_harness.py install --dry-run
python scripts/codex_harness.py backup
python scripts/codex_harness.py sync --dry-run
```

The backup is configuration-only. It does not copy `auth.json`, session databases, chat history, caches, worktrees, or runtime binaries.

`sync` mirrors managed local files into the repository; `config.toml` is intentionally excluded because it is machine-specific. Review the diff before committing other machine-specific values.

## Rollback

List snapshots:

```text
python scripts/codex_harness.py list-backups
```

Rollback latest snapshot:

```text
python scripts/codex_harness.py rollback latest --yes
```

Rollback a specific snapshot:

```text
python scripts/codex_harness.py rollback 20260918-153000 --yes
```

Rollback restores files that existed before install and removes managed files that did not exist before install. Unmanaged user files remain untouched.

## What install changes

Default roots:

- Codex home: `~/.codex`
- User skills: `~/.agents`

Override them with `CODEX_HOME` and `AGENTS_HOME` environment variables. The installer writes:

- `~/.codex/AGENTS.md`
- `~/.codex/agents/`
- `~/.codex/hooks/`
- `~/.agents/skills/`

The install skill separately reviews and merges the core settings from `config/config.toml.template` into `~/.codex/config.toml`, preserving user-specific configuration. Hooks are copied as scripts and templates. They are not activated automatically. Review the platform-specific JSON under `hooks/` before enabling them.

## Security

The template uses safer shared defaults:

- `approval_policy = "on-request"`
- `sandbox_mode = "workspace-write"`

Review before changing these. Do not commit local credentials or backups. Re-authenticate Codex normally on each machine.

Plugins are listed in `plugins/manifest.json`. The harness does not vendor or install plugin files. Install managed plugins through the current Codex/plugin mechanism; do not copy the versioned `.codex/plugins/cache` directory between machines.

## Updating the harness

1. Run `python scripts/codex_harness.py sync --dry-run`.
2. Run `python scripts/codex_harness.py sync --yes` after reviewing the diff.
3. Edit `config/config.toml.template` intentionally when the portable baseline changes; never sync a user's local `config.toml` into it.
4. Review the sync skill's proposed `plugins/manifest.json` update against live Codex plugin state.
5. Run `python scripts/codex_harness.py status`.
6. Commit only intended source changes.

Codex loads repository-only skills from `.agents/skills/`, distributable skills from `skills/`, and instructions from `AGENTS.md`; restart the Codex session after changing user-level configuration.
