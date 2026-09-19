---
name: codex-harness-sync
description: Sync the current local Codex setup back into this repository for maintenance.
disable-model-invocation: true
---

# Sync Codex Harness

Use the repository root as the working directory. Use the available Python command on the machine (`python`, `python3`, or `py -3`) as `PYTHON`.

1. Run `$PYTHON scripts/codex_harness.py status` to identify `CODEX_HOME` and `AGENTS_HOME`.
2. Run `$PYTHON scripts/codex_harness.py sync --dry-run`. Explain that the command copies managed local files into the repository but intentionally excludes `config.toml`.
3. Review the local config as a candidate source for the portable template:
   - Read `$CODEX_HOME/config.toml` and `config/config.toml.template`. If the local file is absent, report that no config candidates are available. Parse both with `tomllib` or `tomli`; report invalid TOML before proposing changes.
   - Compare the full parsed trees, including nested tables and arrays of tables. Classify each local-only or differing setting as a portable candidate, user preference, machine-specific value, runtime/generated state, plugin/marketplace state, or sensitive value.
   - Propose only settings that are useful across installations: shared defaults, stable feature flags, generic agent limits, or portable hook/config behavior. Treat paths, project trust entries, shell/MCP commands, environment values, provider endpoints, model catalogs, timestamps, hook trust/hash state, per-machine UI state, plugin/marketplace state, and credentials/tokens as local-only. Do not print sensitive values; show excluded keys and reasons without copying their contents.
   - Show a minimal proposed diff for `config/config.toml.template`, with each candidate's key, proposed value, and rationale. Never copy the local file wholesale. Ask the human to approve or reject each candidate (batch approval is acceptable); do not edit the template until approval is explicit.
   - Apply only approved candidates with the smallest style-preserving edit. Validate both TOML files after editing. If the human rejects or defers a candidate, leave it local and record that decision.
4. Get separate confirmation for the managed-file sync and the approved template candidates, then run `$PYTHON scripts/codex_harness.py sync --yes`. The command still excludes `config.toml`; template edits are deliberate agent changes, not automatic file copies.
5. Run `git diff --check`, inspect `git diff --stat`, and run `$PYTHON scripts/codex_harness.py status`.
6. Update `plugins/manifest.json` from live Codex plugin state:
   - Read the existing manifest. Treat `enabled_in_source_profile` as the desired profile inventory, not a list of every available marketplace plugin and not a version lock.
   - Inspect `/plugins`, `codex plugin marketplace list` when available, and explicit `[plugins]` enable/disable overrides in the resolved `config.toml`. Do not infer state from `.codex/plugins/cache` alone.
   - Propose additions/removals based on plugins intentionally installed and enabled for this profile. Keep unrelated user plugins outside the manifest. Preserve `install_policy` and notes; never add cache paths or runtime versions.
   - If live state is unavailable or ambiguous, report the ambiguity and ask the human; do not guess. Show the manifest diff and get confirmation before writing it.
   - Write valid JSON, run `$PYTHON -m json.tool plugins/manifest.json`, and report the resulting desired plugin list.
7. Report changed paths, approved and rejected config candidates, and any values the user should remove before committing. Never copy credentials, session databases, chat history, caches, worktrees, or runtime binaries.

Done means the managed sync completed, the local config was compared with the template and every candidate received a human decision, approved template edits were validated, the manifest was reconciled or ambiguity was reported, diff checks pass, and the repository diff was reviewed for local-only values.
