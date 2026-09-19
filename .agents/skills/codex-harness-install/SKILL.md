---
name: codex-harness-install
description: Install this repository's Codex setup after backing up the current local setup.
disable-model-invocation: true
---

# Install Codex Harness

Use the repository root as the working directory. Use the available Python command on the machine (`python`, `python3`, or `py -3`) as `PYTHON`.

The installer scope is deliberately narrow:

- Back up `.codex/AGENTS.md`, `.codex/config.toml`, `.codex/agents/`, `.codex/hooks/`, and `.codex/hooks.json`.
- Back up `.agents/skills/`, `.codex/skills/`, and `.agents/.skill-lock.json`.
- Replace `.codex/AGENTS.md`, `.codex/agents/`, and `.codex/hooks/` from this repository.
- Remove `.codex/hooks.json` only.
- Leave the backed-up skill paths out of the harness file-copy set. Skill collision
  removal and installation use `npx skills` below.
- Do not write `.codex/config.toml`; the agent merges it after install.

Directory backups include the full directory tree. If a directory did not exist, the manifest records `existed = false` and the backup may contain an empty directory marker so rollback removes the newly installed directory.

1. Read `README.md`. Run `$PYTHON scripts/codex_harness.py status` and show the target roots. Confirm that skill paths are backup-only and are not copied from the repository by the Python installer.
2. Run `$PYTHON scripts/codex_harness.py backup`; record the preflight backup ID and path. This happens before any removal or replacement.
3. Run `$PYTHON scripts/codex_harness.py install --dry-run`. Show the copy, replacement, removal, and skill-backup targets plus the preflight backup ID; get confirmation before changing the local setup.
4. Run `$PYTHON scripts/codex_harness.py install --yes`; record the installer-created backup ID too. The command backs up again, removes/replaces only the harness paths, and leaves skill contents to the explicit `npx skills` flow below.
5. Run `$PYTHON scripts/codex_harness.py status` and report both backup IDs, the installed-file count, and replaced/removed path count.
6. Reconcile skills as one explicit, backed-up transaction:
   - Read `skills/remote-skills.json` as a JSON list. Each entry must contain one remote `source`, one `ref`, and its selected `skills`; `ref: "latest"` is allowed only when the sync skill recorded explicit human approval for a moving install.
   - Treat the harness repository's own entry as a remote source too. It must use the repository's published `origin` URL and a commit ref; never install the harness skill set from `./skills`.
   - For each manifest entry, run `npx skills add <source-or-source/tree/ref> --list` and compare the discovered names with that entry's selected names. Report missing, renamed, or unexpected names before changing local skills.
   - Run `npx skills list --global --json`. The collision set is every installed global skill whose name is in either the repository set or the union of names in `skills/remote-skills.json`. Show each collision's name, path, agents, and recorded source. Extras are allowed and stay untouched.
   - Confirm the listed global paths are covered by the roots recorded by
     `status`. The harness `AGENTS_HOME` override is not an `npx skills`
     setting; if the CLI reports another global store, stop before removal and
     report that it needs its own backup scope.
   - After human approval, remove every collision by name from every global agent:

     ```text
     npx --yes skills remove <collision-name> ... --global --agent '*' --yes
     ```

   - Install each remote manifest entry, one `--skill <name>` per entry. For a concrete ref, use the source repository's `/tree/<ref>` URL; for an approved `latest` ref, use the source URL without a ref:

     ```text
     npx --yes skills add <source-or-source/tree/ref> --global --agent '*' --skill <name> ... --yes
     ```

   - `--global` uses the CLI's user-level canonical store. `--agent '*'`
     targets all supported/default agents. Omit `--copy` so the CLI keeps its
     default symlink method. Remote installs update `.agents/.skill-lock.json`
     with source/ref/hash evidence. Do not edit the lock manually or copy skill
     directories into agent paths.
   - If `npx`/Node.js is unavailable, report the exact commands and defer this
     step. Do not remove anything when the collision inventory cannot be read.
7. Merge `.codex/config.toml` with a separate human approval through the agent:
   - Read `config/config.toml.template` as the portable baseline and `$CODEX_HOME/config.toml` as the user's existing config. Resolve `$CODEX_HOME` from `status`; default is `~/.codex`.
   - The installer intentionally does not copy or edit `config.toml`. If the config is missing, propose creating it from the template. If it exists, inspect it fully and produce a minimal merge.
   - Use this as the target baseline, while treating explicit existing values as user-owned:
     - Top level: `approval_policy = "on-request"`, `sandbox_mode = "workspace-write"`, `personality = "pragmatic"`, `web_search = "live"`, `project_doc_max_bytes = 65536`.
     - `[agents]`: `max_depth = 1`, `max_threads = 6`.
     - `[features]`: `apps`, `goals`, `hooks`, `multi_agent`, `undo`, and `workspace_dependencies` enabled.
     - `[desktop]`: `followUpQueueMode = "queue"`, `show-context-window-usage = true`.
     - `[memories]`: `generate_memories = false`, `use_memories = false`.
   - Merge `[[skills.config]]` entries by `name` without duplicates. Preserve explicit user choices when they conflict with the baseline; surface the conflict instead of silently overriding it. Keep optional model pins commented unless the user already chose one.
   - Preserve unrelated settings and machine-specific paths, MCP commands, project trust entries, plugin/marketplace entries, model settings, comments, and formatting where practical. Never replace the whole file just to apply the baseline.
   - Show the proposed config diff and get explicit human approval before writing. Apply the smallest valid edit, then validate the resolved file with an available TOML parser (`tomllib` or `tomli`) and report the changed path.
   - Run `$PYTHON scripts/codex_harness.py status` again after the config merge.
8. Reconcile plugins from `plugins/manifest.json`:
   - Read `enabled_in_source_profile` as the desired plugin inventory. It is not a version lock and does not mean “copy from cache.”
   - Inspect live plugin state in Codex's `/plugins` browser and run `codex plugin marketplace list` when the CLI is available. Inspect explicit `[plugins]` enable/disable overrides in the resolved `config.toml`, but do not infer installed state from `config.toml` or cache alone.
   - Classify every desired entry as installed/enabled, installed/disabled, missing, or not inspectable. Keep unrelated user plugins. Treat an explicit local disable as user intent and report it instead of silently overriding it.
   - Show missing or disabled desired plugins, their marketplace/source, and the proposed official install or enable action. Get explicit human approval before changing plugin state. Use `/plugins` or the current official marketplace mechanism; never copy plugin repositories or `.codex/plugins/cache`.
   - For Ponytail specifically, check `node --version`; report if Node.js is unavailable. Ponytail skills still work without Node.js, but its lifecycle hooks do not. If absent, show the planned commands and wait for approval:

     ```text
     codex plugin marketplace add DietrichGebert/ponytail
     codex plugin add ponytail@ponytail
     ```

     Run the marketplace command only if `DietrichGebert/ponytail` is not already configured. After approval, install Ponytail from that marketplace.
   - After any approved installation, enablement, or hook trust action, recheck `/plugins`, then restart Codex/start a new thread when required. For Ponytail, open `/hooks` and have the human review and trust its two lifecycle hooks.
   - If CLI plugin commands are unavailable, give the human the equivalent Codex UI path: `/plugins` → select the relevant marketplace → install or enable the plugin. For Ponytail, add `https://github.com/DietrichGebert/ponytail` first, then review `/hooks`.
   - Report installed/enabled, installed/disabled, missing, and deferred entries. Do not modify `plugins/manifest.json` during install unless the human explicitly asks for a profile change.
Done means the harness install completed, status succeeds, backup IDs are reported, every `skills/remote-skills.json` entry—including the harness repository's commit-pinned entry—was assessed and installed remotely or clearly deferred, collisions were approved and removed before intended sources were installed, config merge is approved and valid or explicitly deferred, and every desired plugin is classified with approved changes completed or clearly deferred.
