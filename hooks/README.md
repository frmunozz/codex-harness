# Optional hooks

`session_start.py` is configured through the inline `[[hooks.SessionStart]]`
entry in `config/config.toml.template` and merged into the user's config by
the install skill.

Do not add a sibling `hooks.json` at the same config layer. Codex merges both
representations and warns at startup.

The runner scripts keep command invocation portable across Windows and Unix.
