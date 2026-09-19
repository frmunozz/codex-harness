---
name: codex-harness-remote-update
description: Review and update skills tracked in skills/remote-skills.json by choosing newer commits or tags for the repository, the local developer setup, or both.
---

# Update Remote Codex Skills

Use the repository root. Use the available Python command (`python`, `python3`,
or `py -3`) as `PYTHON`. This skill changes repository metadata and/or the
developer's global skills; discovery and human approval happen before either
mutation.

1. Run `$PYTHON scripts/codex_harness.py status`. Read and validate
   `skills/remote-skills.json` as a list of `{source, ref, skills}` records.
   Resolve `CODEX_HOME` and `AGENTS_HOME` from `status`; never infer roots from
   shell defaults. Read `$AGENTS_HOME/.skill-lock.json` and
   `npx skills list --global --json` when available. Treat lock entries as
   evidence only; never edit the lock manually.
2. For every manifest record, resolve the current ref to a commit and inspect
   the remote repository:
   - Use `git ls-remote` for the current ref, default-branch `HEAD`, and tags.
   - Use a temporary shallow/filtered clone or the provider's read-only API
     when ancestry, commit dates, or tag ordering cannot be established from
     `ls-remote`. Keep the temporary checkout outside the repository and
     delete it after inspection.
   - Identify the newest reachable commit and the newest meaningful tag. Use
     semantic ordering for semantic-version tags; if tags are non-semantic or
     ordering is ambiguous, show the candidates and ask the human rather than
     guessing.
   - Compare the selected ref with the lock's `source`, `ref`, `skillPath`,
     and `skillFolderHash`. A folder hash proves content identity, not a
     version. Report missing/legacy lock refs and source mismatches.
3. Show one proposal table per remote pack:

   ```text
   source | current ref/commit | newest commit | newest tag/commit | skills
   ```

   For each pack, ask the human to choose:
   - keep current;
   - newest commit, recorded as the full commit SHA;
   - newest tag, recorded as the tag name; or
   - a specific displayed tag/commit.

   Also ask where to apply the choice: repository manifest, local developer
   setup, both, or neither. A newer commit and a newer tag are separate choices;
   do not silently prefer one. `latest` is not a version choice when a concrete
   commit or tag is available. If no concrete ref can be established, require
   explicit approval before recording `ref: "latest"`.
4. After approval, apply local updates first when the local target is selected:
   - Run `$PYTHON scripts/codex_harness.py backup`; record the backup ID before
     removing anything.
   - For each affected pack, remove only its selected skill names from the
     global agents, then add the same names from the selected source/ref. Use
     the current `npx skills` syntax; for GitHub tree refs the source is
     `<source>/tree/<ref>`, and for generic Git sources use the CLI's supported
     `source#ref` form. Example:

     ```text
     npx skills remove --global --agent '*' --yes <skill> ...
     npx skills add <source-or-source/tree/ref> --global --agent '*' --skill <skill> ... --yes
     ```

   - Never install the harness repository from `./skills`; use its published
     remote URL and selected commit. Never run `npx skills update` for a ref
     change; remove/add is deliberate so the lock records the selected ref.
   - Re-read the lock and list output. Confirm source, selected ref, skill
     paths, and folder hashes for every affected skill. If add fails, stop and
     offer `codex-harness-rollback <backup-id>`; do not hand-edit the lock.
5. If the repository target is selected, update only the matching `ref` in
   `skills/remote-skills.json`; keep source and selected skill names unchanged.
   Record full commit SHAs for commit choices. For this harness repository,
   use only commits already published at `origin`; never point the manifest at
   an uncommitted or unpushed worktree state. Show the manifest diff, validate
   it with `$PYTHON -m json.tool skills/remote-skills.json`, and report the
   previous ref for rollback.
   - If only the local target is selected, leave the manifest unchanged and
     report that a later harness install will restore its recorded ref. If only
     the repository target is selected, leave the local setup unchanged and
     report that it remains on its previous ref until reinstalled.
6. Run `git diff --check`, inspect `git diff --stat`, run
   `$PYTHON scripts/codex_harness.py status`, and report:
   - each pack's old/new ref and selected target;
   - local install and lock verification results;
   - the backup ID when local files changed;
   - repository manifest changes and any deferred/ambiguous choices.

Done means every manifest record was checked, every update choice and target
was explicit, selected local installs match the lock, selected repository refs
are valid JSON and published, and rollback information is reported.
