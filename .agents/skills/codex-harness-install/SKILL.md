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
7. Recommend Ponytail as a post-install step:
   - Check `node --version`; report if Node.js is unavailable. Ponytail skills still work without Node.js, but its lifecycle hooks do not.
   - Check configured marketplaces with `codex plugin marketplace list`, then open `/plugins` in Codex and search for Ponytail. If Ponytail is already installed, report its state/version and skip installation.
   - If Ponytail is absent, explain that the next action changes the user's plugin configuration and requires explicit human approval. Do not run it yet. Show the planned commands:

     ```text
     codex plugin marketplace add DietrichGebert/ponytail
     codex plugin add ponytail@ponytail
     ```

     Run the marketplace command only if `DietrichGebert/ponytail` is not already configured. After approval, install Ponytail from that marketplace; do not copy the repository, the old offline snapshot, or `.codex/plugins/cache`.
   - After approval and installation, open `/hooks`, have the human review and trust Ponytail's two lifecycle hooks, then restart Codex/start a new thread. Confirm Ponytail appears installed in `/plugins`.
   - If CLI plugin commands are unavailable, give the human the equivalent Codex UI path: `/plugins` → add the `https://github.com/DietrichGebert/ponytail` marketplace → install Ponytail → review `/hooks`.

Done means the harness install completed, status succeeds, backup IDs are reported, config merge is approved and valid or explicitly deferred, and Ponytail is either already installed, installed after explicit approval, or explicitly deferred by the human.
