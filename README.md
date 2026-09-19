# Codex Harness

Portable, experimental Codex user configuration for Windows, macOS, and Linux.

Contents:

- `skills/` — shared skills. Codex can load these directly when working in this repository.
- `agents/` — reusable subagent presets.
- `instructions/` — global `AGENTS.md` guidance.
- `hooks/` — cross-platform hook scripts and activation templates.
- `config/config.toml.template` — safe portable configuration template.
- `plugins/manifest.json` — plugin inventory and source notes.
- `plugins/ponytail/` — offline Ponytail source snapshot.
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

The installer backs up managed existing files first. Backups go to `backup/<timestamp>/`; `.gitignore` prevents them from entering Git.

## Preview and backup

```text
python scripts/codex_harness.py status
python scripts/codex_harness.py install --dry-run
python scripts/codex_harness.py backup
python scripts/codex_harness.py sync --dry-run
```

The backup is configuration-only. It does not copy `auth.json`, session databases, chat history, caches, worktrees, or runtime binaries.

`sync` mirrors managed local files into the repository; review the diff before committing machine-specific values.

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
- `~/.codex/config.toml`
- `~/.codex/agents/`
- `~/.codex/hooks/`
- `~/.agents/skills/`

Hooks are copied as scripts and templates. They are not activated automatically. Review the platform-specific JSON under `hooks/` before enabling them.

## Security

The template uses safer shared defaults:

- `approval_policy = "on-request"`
- `sandbox_mode = "workspace-write"`

Review before changing these. Do not commit local credentials or backups. Re-authenticate Codex normally on each machine.

Plugins are listed in `plugins/manifest.json`. Managed OpenAI plugins should be installed through the current Codex/plugin mechanism. Do not copy the versioned `.codex/plugins/cache` directory between machines.

## Updating the harness

1. Run `python scripts/codex_harness.py sync --dry-run`.
2. Run `python scripts/codex_harness.py sync --yes` after reviewing the diff.
3. Run `python scripts/codex_harness.py status`.
4. Commit only intended source changes.

Codex loads repository skills from `skills/` and instructions from `AGENTS.md`; restart the Codex session after changing user-level configuration.
