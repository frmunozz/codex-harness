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

Done means the install completed, status succeeds, and the backup ID is reported.
