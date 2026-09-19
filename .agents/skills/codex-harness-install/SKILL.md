---
name: codex-harness-install
description: Install this repository's Codex setup after backing up the current local setup.
disable-model-invocation: true
---

# Install Codex Harness

Use the repository root as the working directory. Use the available Python command on the machine (`python`, `python3`, or `py -3`) as `PYTHON`.

1. Read `README.md`. Run `$PYTHON scripts/codex_harness.py status` and show the target roots.
2. Run `$PYTHON scripts/codex_harness.py backup`; record the preflight backup ID and path.
3. Run `$PYTHON scripts/codex_harness.py install --dry-run`. Show the targets and preflight backup ID; get confirmation before changing the local setup.
4. Run `$PYTHON scripts/codex_harness.py install --yes`; record the installer-created backup ID too.
5. Run `$PYTHON scripts/codex_harness.py status` and report both backup IDs, the installed-file count, and any removed legacy files.
6. Merge the Codex config with a separate human approval:
   - Read `config/config.toml.template` as the portable baseline and `$CODEX_HOME/config.toml` as the user's existing config. Resolve `$CODEX_HOME` from `status`; default is `~/.codex`.
   - The script intentionally does not copy the template into `config.toml`. If the config is missing, propose creating it from the template. If it exists, inspect it fully and produce a minimal merge.
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
7. Reconcile plugins from `plugins/manifest.json`:
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

Done means the harness install completed, status succeeds, backup IDs are reported, config merge is approved and valid or explicitly deferred, and every desired plugin is classified with approved changes completed or clearly deferred.
