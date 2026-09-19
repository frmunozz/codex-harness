# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project intends to follow [Semantic Versioning](https://semver.org/).
No tagged release exists yet, so the reconstructed history remains under
`Unreleased` until the first release.

## [Unreleased]

### Added

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

- **2026-09-19:** Removed the committed skill lock and obsolete skill copies
  while retaining the source trees needed for installation.
- **2026-09-19:** Removed the vendored Ponytail plugin snapshot; plugin state is
  represented by the manifest and managed through the official plugin flow.
- **2026-09-18:** Removed legacy RTK/Caveman instructions, hooks, and prompts.

[Unreleased]: https://github.com/frmunozz/codex-harness/compare/67bd154...HEAD
