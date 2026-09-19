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
5. Discover and reconcile user-level skills:
   - Enumerate skill directories under `$AGENTS_HOME/skills/` and `$CODEX_HOME/skills/`, using the roots reported by `status`. Read each `SKILL.md` frontmatter and record its skill name, complete relative file tree, and content hash. Ignore `.system`, caches, `.git`, `__pycache__`, compiled files, credentials, and runtime binaries.
   - Read `$AGENTS_HOME/.skill-lock.json` when present. Treat its `source`, `sourceUrl`, `skillPath`, and `skillFolderHash` as provenance and integrity evidence for skills installed through `npx skills`; never copy or edit the lock file. A folder hash is not a release tag or commit.
   - Inventory repository skills from `skills/**/SKILL.md` and remote records from `skills/remote-skills.json`. Compare local, repository, lock, and remote inventories by skill name. Report matching skills, missing skills, content drift, stale lock entries, and local extras.
   - Ensure `skills/remote-skills.json` contains one entry for this harness repository, using its published `origin` URL, a full commit ref, and every distributable skill under `skills/**/SKILL.md`. Never use `./skills` as the install source. If the worktree has new skill content that is not published yet, report the pending self-reference and defer changing the harness ref until that commit exists on the remote.
   - For every lock-backed remote skill absent from `skills/remote-skills.json`, determine its source repository and an exact tag or commit. Check installed-source metadata and repository refs when available; do not infer a version from `skillFolderHash`. Group skills into one record per source/ref pair using this shape:

     ```json
     {
       "source": "https://github.com/owner/repo",
       "ref": "v1.2.3",
       "skills": ["skill-name"]
     }
     ```

   - Show the proposed `skills/remote-skills.json` diff. If no concrete tag or commit can be established, propose `"ref": "latest"` only after explicitly asking the human whether a moving latest install is acceptable. Record the approval before writing; never silently convert an unknown version to `latest`.
   - For new local skills without remote provenance, compare their content with the repository inventory. Copy new developer-authored skills into `skills/custom/<name>/` and clearly OpenAI-provided skills into `skills/codex-app/<name>/`, using source metadata or package/plugin evidence; a `.codex/skills` path alone is not proof of OpenAI origin. Preserve supporting references, scripts, assets, and agent metadata while excluding caches, credentials, and runtime binaries. If origin is ambiguous, ask the human before copying. Existing repository skills with drift require review; do not overwrite them silently.
   - Do not vendor remote skill content. Remote skills belong in `skills/remote-skills.json`; custom and OpenAI skills belong in the repository tree. Validate the JSON with `$PYTHON -m json.tool skills/remote-skills.json` after approved edits.
6. Run `git diff --check`, inspect `git diff --stat`, and run `$PYTHON scripts/codex_harness.py status`.
7. Update `plugins/manifest.json` from live Codex plugin state:
   - Read the existing manifest. Treat `enabled_in_source_profile` as the desired profile inventory, not a list of every available marketplace plugin and not a version lock.
   - Inspect `/plugins`, `codex plugin marketplace list` when available, and explicit `[plugins]` enable/disable overrides in the resolved `config.toml`. Do not infer state from `.codex/plugins/cache` alone.
   - Propose additions/removals based on plugins intentionally installed and enabled for this profile. Keep unrelated user plugins outside the manifest. Preserve `install_policy` and notes; never add cache paths or runtime versions.
   - If live state is unavailable or ambiguous, report the ambiguity and ask the human; do not guess. Show the manifest diff and get confirmation before writing it.
   - Write valid JSON, run `$PYTHON -m json.tool plugins/manifest.json`, and report the resulting desired plugin list.
8. Report changed paths, approved and rejected config and skill candidates, provenance gaps, stale lock entries, and any values the user should remove before committing. Never copy credentials, session databases, chat history, caches, worktrees, or runtime binaries.

Done means the managed sync completed, the local config was compared with the template and every candidate received a human decision, local skills were inventoried against repository and lock state, approved remote/custom/OpenAI changes were validated, the plugin manifest was reconciled or ambiguity was reported, diff checks pass, and the repository diff was reviewed for local-only values.
