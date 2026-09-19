# Codex Harness

Portable, experimental Codex user configuration for Windows, macOS, and Linux.

Contents:

- `skills/` — repository skill source installed through the commit-pinned entry in `skills/remote-skills.json`.
- `.agents/skills/` — repository-only maintenance skills; never installed globally.
- `agents/` — reusable subagent presets.
- `instructions/` — global `AGENTS.md` guidance.
- `hooks/` — cross-platform hook scripts and activation templates.
- `config/config.toml.template` — safe portable configuration baseline for the install skill.
- `plugins/manifest.json` — desired plugin inventory and source notes; install/sync skills reconcile it with live plugin state.
- `skills/remote-skills.json` — remote skill sources, refs, and selected skill names for reproducible install.
- `docs/recommendations.md` — recommendation policy used by the audit skill.
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

The installer backs up existing scoped files and directory trees first. It also backs up `config.toml`, both skill trees, and `.agents/.skill-lock.json` for rollback, but never edits `config.toml`; the install skill reviews and merges the config baseline through the agent after human approval. Backups go to `backup/<timestamp>/`; `.gitignore` prevents them from entering Git.

The installer copies harness files only. The install skill separately assesses the expected skill names, removes approved collisions through `npx skills`, then installs the remote entries from `skills/remote-skills.json` and this repository's skills with global symlinks.

## Optional OpenCodex integration

OpenCodex is an optional local provider proxy. It is separate from the core harness and is not installed, configured, or managed by this repository. It can keep the ChatGPT provider available while exposing optional API-key providers such as DeepSeek or AWS Bedrock through Codex.

See [`docs/opencodex.md`](docs/opencodex.md) for installation, provider setup, fallback routing, validation, and cleanup.

## Preview and backup

```text
python scripts/codex_harness.py status
python scripts/codex_harness.py install --dry-run
python scripts/codex_harness.py backup
python scripts/codex_harness.py sync --dry-run
```

Audit the current local setup without changing it by running
`/codex-harness-audit`. It compares managed files, config, plugins, imported
skills, freshness, and deprecated RTK/Caveman residue against
[`docs/recommendations.md`](docs/recommendations.md), then routes approved
changes to the existing maintenance skills.

The backup contains configuration plus the two skill stores and the skills lock. It does not copy `auth.json`, session databases, chat history, caches, worktrees, or runtime binaries.

`sync` mirrors managed local files into the repository; its executable intentionally excludes `config.toml`. The sync skill compares the local config with the template, proposes portable candidates, and requires explicit human approval before adding any selected settings to `config/config.toml.template`. Paths, trust entries, commands, runtime/plugin state, and secrets remain local. Review the diff before committing.

## Rollback

List snapshots:

```text
python scripts/codex_harness.py list-backups
```

Rollback a specific snapshot:

```text
python scripts/codex_harness.py rollback 20260918-153000 --yes
```

Rollback requires an explicitly selected backup ID. It restores the selected manifest, including `config.toml`, and removes paths recorded as absent. Unmanaged user files remain untouched.

## What install changes

Default roots:

- Codex home: `~/.codex`
- User skills: `~/.agents`

Override them with `CODEX_HOME` and `AGENTS_HOME` environment variables. The installer backs up:

- `~/.codex/AGENTS.md`
- `~/.codex/config.toml`
- `~/.codex/agents/`
- `~/.codex/hooks/`
- `~/.codex/hooks.json`
- `~/.agents/skills/`
- `~/.codex/skills/`
- `~/.agents/.skill-lock.json`

The installer replaces `~/.codex/AGENTS.md`, `~/.codex/agents/`, and `~/.codex/hooks/`. It removes `~/.codex/hooks.json`. Skill paths are backup-only for the Python installer; the install skill handles approved collision removal and `npx skills add` installation. The install skill separately reviews and merges the core settings and inline hooks from `config/config.toml.template` into `~/.codex/config.toml`, preserving user-specific configuration. Hook scripts are copied but not activated automatically; review the proposed config merge before enabling them.

## Skills

From the repository root, use the install skill to assess the expected skill set, remove approved collisions, and install repository skills plus the remote skills declared in `skills/remote-skills.json`.

Repository skills:

```text
npx --yes skills add <harness-source/tree/commit> --global --agent '*' --skill <name> ... --yes
```

The harness source and commit are the first entry in
[`skills/remote-skills.json`](skills/remote-skills.json); use the install skill
to expand the selected names. Do not install repository skills from `./skills`.

Remote skills: read [`skills/remote-skills.json`](skills/remote-skills.json). Each list entry groups one source and ref with selected names, including this harness repository at a published commit. Use the source repository's `/tree/<ref>` URL for a concrete ref, or the source URL for an explicitly human-approved `latest` entry. Install with repeated `--skill` options, `--global --agent '*'`, and no `--copy`; remove only approved collisions with expected names. Unrelated extra skills remain.

## Security

The template uses safer shared defaults:

- `approval_policy = "on-request"`
- `sandbox_mode = "workspace-write"`

Review before changing these. Do not commit local credentials or backups. Re-authenticate Codex normally on each machine.

Plugins are listed in `plugins/manifest.json`. The harness does not vendor or install plugin files. Install managed plugins through the current Codex/plugin mechanism; do not copy the versioned `.codex/plugins/cache` directory between machines.

## Updating the harness

1. Run `python scripts/codex_harness.py sync --dry-run`.
2. Let the sync skill compare local `config.toml` with the template and show a redacted proposal for portable candidates.
3. Let the sync skill inventory `$AGENTS_HOME/skills/`, `$CODEX_HOME/skills/`, and `.agents/.skill-lock.json` against repository and remote skill inventories.
4. Approve or reject config and remote-version candidates explicitly; copy new custom/OpenAI skills into the repository tree as directed. Never sync a user's local `config.toml` wholesale or vendor remote skill content.
5. Run `python scripts/codex_harness.py sync --yes` after reviewing the managed-file diff.
6. Run `/codex-harness-remote-update` when choosing newer commits/tags for tracked packs.
7. Review the sync skill's proposed `plugins/manifest.json` update against live Codex plugin state.
8. Run `python scripts/codex_harness.py status`.
9. Commit only intended source changes.

Run `/codex-harness-audit` after updating or installing the harness.

Codex loads skills from the global `.agents/skills/` canonical store and agent links; restart the Codex session after changing user-level configuration.
