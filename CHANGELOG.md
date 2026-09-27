# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project intends to follow [Semantic Versioning](https://semver.org/).
No tagged release exists yet, so the reconstructed history remains under
`Unreleased` until the first release.

## [Unreleased]

### Added

- **2026-09-26:** Added the explicit `pr-review-loop` skill and read-only Astra
  `review-triage` agent for bounded review iterations, evidence-based finding
  dispositions, local fix commits, and a per-iteration Scope/Drift gate.
- **2026-09-19:** Added the harness-owned `git-commit` skill with supporting
  agent metadata for reviewable Conventional Commit workflows.
- **2026-09-19:** Added the read-only `codex-harness-audit` skill, policy
  recommendations, optional OpenCodex documentation, pinned Matt Pocock skill
  metadata, and explicit plugin/configuration reconciliation guidance.
- **2026-09-19:** Added plugin manifest reconciliation rules and approval-gated
  live plugin classification during harness setup.
- **2026-09-18:** Added the portable cross-platform Codex harness, including
  configuration, agents, hooks, skills, plugin metadata, and
  backup/install/status/sync/rollback tooling.
- **2026-09-19:** Added this changelog and repository instructions for keeping
  it current.

### Changed

- **2026-09-27:** Updated `pr-review-loop` to pin Native Codex reviews to
  GPT-6 Sol at high reasoning effort, pause for a human checkpoint after 20
  minutes, and avoid automatic retries; reconciled plugin IDs and the harness
  source URL, then advanced the harness pin to the published review-loop
  commit.
- **2026-09-26:** Advanced the pinned harness skill source to the published
  commit containing `pr-review-loop`.
- **2026-09-26:** Migrated the deep-worker profile to GPT-6 Sol and the
  reviewer/explorer profiles to GPT-6 Luna, using Luna's supported `max`
  reasoning effort; set review-triage to Astra `low` reasoning.
- **2026-09-20:** Updated the install config baseline to use
  `max_concurrent_threads_per_session = 12` instead of deprecated
  `max_threads`.
- **2026-09-20:** Refined global response-style guidance to favor concise,
  direct, low-filler technical communication without reducing reasoning depth,
  validation, clarity, or required detail.
- **2026-09-20:** Broadened advisor orchestration to cover high-impact decision
  and validation checkpoints, added bounded clarification dialogue and
  consultation-scoped agent cleanup, raised Astra advisor reasoning to medium,
  and increased the portable concurrent-subagent limit to 12.
- **2026-09-19:** Added commit-pinned remote tracking for the harness skill
  source and a human-approved updater skill for selecting newer commits or
  tags on the repository, local setup, or both.
- **2026-09-19:** Standardized remote skill provisioning in
  `skills/remote-skills.json` and extended sync guidance to discover local
  skills, lock-file provenance, concrete refs, and approved latest installs.
- **2026-09-19:** Extended sync guidance to compare the developer's local
  `config.toml` with the portable template, propose safe candidates, and require
  explicit human approval before adding selected settings.
- **2026-09-19:** Made configuration merging agent-guided and backup-only;
  preserved user-owned configuration while clarifying install boundaries.
- **2026-09-19:** Hardened backup, install, rollback, and sync behavior for
  directories and symlinks; added target-kind validation and required explicit
  backup IDs.
- **2026-09-19:** Separated distributable skills from repository-only custom
  skills and externally pinned skills; consolidated the active skill layout.
- **2026-09-19:** Replaced duplicate platform hook JSON with inline,
  cross-platform `SessionStart` configuration and portable runner scripts.
- **2026-09-18:** Simplified the portable skill layout, added sync support, and
  narrowed legacy cleanup to approved paths.

### Removed

- **2026-09-19:** Removed the unused `sites` plugin from the desired source
  profile manifest.
- **2026-09-19:** Removed the committed skill lock and obsolete skill copies
  while retaining the source trees needed for installation.
- **2026-09-19:** Removed the vendored Ponytail plugin snapshot; plugin state is
  represented by the manifest and managed through the official plugin flow.
- **2026-09-18:** Removed legacy RTK/Caveman instructions, hooks, and prompts.

[Unreleased]: https://github.com/frmunozz/codex-harness/compare/67bd154...HEAD
