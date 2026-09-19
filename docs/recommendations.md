# Codex Harness Recommendations

Policy source for `codex-harness-audit`. Update this document when the
recommended setup changes. The audit reports policy; the install, backup,
rollback, and sync skills perform approved changes.

## Source of truth

- `README.md`: human-facing scope, safety boundary, and commands.
- `scripts/codex_harness.py`: file-copy, backup, sync, and rollback behavior.
- `config/config.toml.template`: portable configuration baseline.
- `plugins/manifest.json`: desired plugin inventory, not a version lock or
  plugin-cache mirror.
- `skills/remote-skills.json`: remote skill sources, refs, and selected names.
- `skills/`: repository skill source installed through the commit-pinned remote
  entry in `skills/remote-skills.json`.
- `.agents/skills/`: repository-only maintenance skills. They are not part of
  the repository skill source or the harness file-copy target.

When these files disagree about behavior, use `README.md` and the executable
script for mechanics, and this document for recommendations.

## Recommended setup

### Keep the harness current

Use a clean, current checkout of this repository. Run the audit after an
install, after a harness update, and when Codex behavior looks different from
the documented setup.

The managed local paths should match the repository sources:

| Local path | Repository source |
| --- | --- |
| `$CODEX_HOME/AGENTS.md` | `instructions/AGENTS.md` |
| `$CODEX_HOME/agents/` | `agents/` |
| `$CODEX_HOME/hooks/` | `hooks/` |

`$AGENTS_HOME/skills/` and `$CODEX_HOME/skills/` are user skill stores. The
harness backs up both trees and `$AGENTS_HOME/.skill-lock.json`; the install
skill removes only approved name collisions before `npx skills add` recreates
the expected set. Rollback restores the selected trees and lock file together.

`$CODEX_HOME/config.toml` is user-owned. Compare it with the template baseline,
then merge only missing or intentionally approved settings. Preserve user
choices, comments, machine paths, trust entries, model settings, and unrelated
MCP/plugin configuration.

### Keep Ponytail available

`ponytail@ponytail` is part of the desired plugin profile. Verify it through
live Codex plugin state, not through `.codex/plugins/cache` or `config.toml`.
If missing or disabled, report the official install or enable path and wait for
approval. Do not vendor or copy the plugin cache.

Ponytail skills work without Node.js. Its lifecycle hooks require Node.js and
separate human review/trust.

### Keep remote skills coherent

Remote skills are external skills, not a harness plugin-cache mirror. Use
`skills/remote-skills.json` as the expected inventory and configured ref. The
audit expected set is the union of that manifest and the names discovered by
`npx skills add <source-or-source/tree/ref> --list`. Missing or wrong-source
expected skills are actionable; extra developer skills are valid. The install
skill backs up, shows, and removes approved collisions, then installs each
configured remote source. Do not expect remote skill source folders inside
this repository. A `latest` ref is a moving target and requires explicit human
approval. Use `/codex-harness-remote-update` to choose and apply newer tags or
commits to the local setup, the manifest, or both.

## Remove or avoid

### RTK and Caveman

RTK and Caveman are no longer recommended for this harness. Audit for both
active references and legacy files:

- `rtk` or `caveman` in `AGENTS.md`, skills, hooks, prompts, or config;
- `.codex/RTK.md`;
- `.codex/CAVEMAN_FULL.md` or `.codex/CAVEMAN_ULTRA.md`;
- `.codex/hooks/rtk_enforce.py`;
- `$AGENTS_HOME/skills/caveman/`;
- old RTK/Caveman instructions copied into another managed file.

Report exact paths and references. Recommend removing stale instructions and
legacy harness files after review. Do not uninstall a global executable or
delete arbitrary user files automatically.

### State and cache copying

Never copy credentials, `auth.json`, session databases, chat history, caches,
worktrees, runtime binaries, or versioned plugin caches between machines.
Do not replace a user's full `config.toml` with the repository template.

### Legacy Codex paths

Flag unexpected legacy state such as `.codex/hooks.json` when present. The
current installer removes that exact path within its approved scope. Treat
`.codex/skills/` and `$AGENTS_HOME/skills/` as user-owned state: backup and
rollback are explicit, while skill replacement requires the install skill's
collision report and approval.

## Finding severity

- **Blocker**: invalid config, unsafe target root, missing source required to
  reason about the install, or a condition that could cause data loss.
- **Action**: managed drift, stale harness checkout, missing desired plugin,
  missing/stale locked skill, or active RTK/Caveman residue.
- **Info**: optional integration, unavailable plugin inspection, user-owned
  customization, or a choice that is valid but differs from the baseline.

Every finding needs evidence: path, command output, hash/diff, plugin-state
classification, or an explicit unavailable check. Recommendations must point
to the next existing skill or documented command.
