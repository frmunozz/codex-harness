---
name: codex-harness-audit
description: Audit the current local Codex setup against this harness repository and its documented recommendations.
disable-model-invocation: true
---

# Audit Codex Harness

Read-only assessment. Do not install, remove, edit, sync, trust hooks, or
change plugin state during this skill. Use the repository root as the working
directory. Read `README.md` and `docs/recommendations.md` first; the latter is
the policy source for the checks below.

## 1. Establish scope

Use the available Python command on the machine (`python`, `python3`, or
`py -3`) as `PYTHON`.

Read these sources before assessing state:

- `README.md`
- `docs/recommendations.md`
- `plugins/manifest.json`
- `skills/remote-skills.json`
- `config/config.toml.template`
- `scripts/codex_harness.py`

Run `$PYTHON scripts/codex_harness.py status`. Record `CODEX_HOME`,
`AGENTS_HOME`, managed-file count, and available backup IDs. Do not infer these
paths from shell defaults when `status` reports different roots.

Completion criterion: repository policy, executable scope, and local roots are
recorded, or the exact unavailable source/check is reported.

## 2. Check harness freshness

Record:

```text
git status --short
git log -1 --format="%H %ad %s" --date=iso
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
```

If an upstream exists and network access is available, use a read-only remote
check such as `git fetch --dry-run`, then report whether the checkout may be
behind its upstream. If no upstream or network is available, say so.

Treat a dirty checkout as a finding: it cannot prove that the source is the
latest published harness. Do not recommend install until the user understands
which source changes are intentional.

Completion criterion: checkout freshness is classified as current, possibly
behind, dirty/ambiguous, or unavailable, with evidence.

## 3. Compare managed files

Compare regular-file maps, relative paths, and SHA-256 hashes for each mapping:

| Local target | Repository source |
| --- | --- |
| `$CODEX_HOME/AGENTS.md` | `instructions/AGENTS.md` |
| `$CODEX_HOME/agents/` | `agents/` |
| `$CODEX_HOME/hooks/` | `hooks/` |

Treat `$AGENTS_HOME/skills/` and `$CODEX_HOME/skills/` as user-owned skill
stores outside the harness file map. Inspect them separately in section 5.
Ignore `.git` and `__pycache__`, matching the harness script. Report missing,
changed, and extra files separately. A changed local file may be an intentional
user customization; label it as drift, not proof of corruption. Never overwrite
it during the audit.

Use a read-only Python snippet, `Get-FileHash`, `sha256sum`, or an equivalent
existing tool. Do not add a temporary audit script to the repository.

Completion criterion: every mapping has a complete missing/changed/extra
result, or an explicit reason it could not be compared.

## 4. Assess configuration

Parse `$CODEX_HOME/config.toml` with `tomllib` or `tomli` when present. Report
invalid TOML immediately as a Blocker. If the file is absent, report that the
baseline merge is missing; do not create it.

Read the template and compare its portable baseline keys, inline hooks, and
feature settings. Preserve explicit user values as user-owned. Classify each
difference as:

- missing baseline value;
- conflicting user value;
- matching baseline;
- unrelated user configuration; or
- unable to inspect.

Check for stale hook/config representations, especially `.codex/hooks.json`,
and for RTK/Caveman references anywhere in the config. Skill directories are
user-owned and are not stale harness paths.

Completion criterion: config syntax, baseline differences, user-owned
conflicts, and legacy paths are all classified.

## 5. Assess plugins and skills

Read `plugins/manifest.json`. Treat `enabled_in_source_profile` as the desired
inventory, not proof of installation. Inspect live Codex plugin state in
`/plugins`; run `codex plugin marketplace list` when the CLI is available.
Classify every desired entry as installed/enabled, installed/disabled, missing,
or not inspectable. Keep unrelated user plugins out of the report except as
context. Do not infer live state from `config.toml` or `.codex/plugins/cache`.

For Ponytail, report Node.js availability separately because skills work
without it while lifecycle hooks do not. Recommend the existing approval-gated
install/enable path; do not run it from this audit.

Read `skills/remote-skills.json`. Enumerate repository names from
`skills/**/SKILL.md`, then run `npx skills add <source-or-source/tree/ref>
--list` for each remote manifest entry and run `npx skills list --global
--json`. The expected set is the union of the repository names and the remote
manifest names. This is a minimum: extra developer skills are valid and must
not be treated as drift. The harness repository entry must use its published
remote URL and a commit ref; a local-path install is drift.

Using the roots reported by `status`, enumerate `$AGENTS_HOME/skills/` and
`$CODEX_HOME/skills/`, and read `$AGENTS_HOME/.skill-lock.json` when present.
Use lock entries to identify `npx skills` provenance and report stale lock
entries, missing local folders, and local skills absent from the repository or
remote manifest. Do not copy or edit the lock during an audit.

For every expected name, classify it as:

- present with the expected source and available to Codex;
- present but sourced from the wrong place, linked to the wrong path, or with
  content that differs from the repository copy;
- present as a remote skill but the CLI cannot attest the configured ref; or
- missing locally.

For repository skills, compare the installed `SKILL.md` content with the
matching file discovered under this repository's `skills/` tree when the
source field is null, because local-path installs are recorded without a
remote source. For remote skills, require `source`/`sourceUrl` to identify the
configured repository. Compare the configured `ref` with lock/source evidence
when available; the list JSON and older lock entries may omit the ref. Report
`ref: "latest"` as an explicitly approved moving target, not as a pinned
version. Otherwise report the configured ref as unverifiable rather than
claiming alignment. A ref check requires an explicit reinstall from the
configured URL or another recorded content hash.

Use the paths returned by `npx skills list` as the live evidence. Do not assume
the harness `AGENTS_HOME` override changes the CLI's own global home; report a
root mismatch as an audit blocker because the install backup would not cover
that store.

Also report extra skills as informational context only. Never remove or
replace them during an audit.

Do not silently update the manifest, install, remove, or fetch upstream skills.

Completion criterion: desired plugins and every expected skill are fully
classified with evidence; no expected skill is missing or wrong, while extra
skills remain acceptable and untouched.

## 6. Scan for deprecated residue

Search the local managed roots and relevant configuration for case-insensitive
`rtk` and `caveman`. Check the legacy paths listed in
`docs/recommendations.md`. Distinguish:

- active instruction/config references;
- stale files or skill directories;
- an installed global executable with no harness reference; and
- no evidence.

Recommend removal of stale instructions and legacy files. Do not uninstall
software or delete user files automatically.

When OpenCodex is present, read `docs/opencodex.md` and keep its provider state
outside the harness audit's managed scope.

Completion criterion: each deprecated item is evidenced, absent, or explicitly
not inspectable.

## 7. Report and route next steps

Lead with a compact status: `aligned`, `aligned with notes`, `action needed`,
or `blocked`. Then report findings in this shape:

```text
[severity] finding
Evidence: path/command/state
Action: next existing skill or documented command
Approval: whether the action changes local state
```

Order actions by safety and dependency:

1. resolve Blockers and unsafe roots;
2. update the harness checkout if it is behind, then rerun the audit;
3. run `codex-harness-install` for approved managed-file drift;
4. use the install skill for the human-approved config merge;
5. use the install/plugin path for missing or disabled desired plugins;
6. use `codex-harness-install` to remove approved collisions and reinstall the
   expected Matt and repository skill sets;
7. remove RTK/Caveman and other legacy residue after review;
8. leave valid user customizations and optional integrations alone.

Do not execute these actions as part of the audit. Ask the user to choose the
next approved skill when a finding requires a mutation.

Done means every source, local root, managed mapping, config baseline,
desired-plugin entry, locked Matt Pocock skill, freshness signal, and
deprecated-residue check is classified; every finding has evidence and a next
step; and no local state was changed.
