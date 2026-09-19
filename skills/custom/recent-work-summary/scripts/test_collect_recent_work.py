"""Unit tests for the recent work collector helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import collect_recent_work as crw


class CollectRecentWorkTests(unittest.TestCase):
    """Cover helper behavior that is easy to regress."""

    def test_normalize_git_path_rename(self) -> None:
        """Keep the destination side of git rename output."""

        raw_path = "client/{old-name.ts => new-name.ts}"
        self.assertEqual(
            crw.normalize_git_path(raw_path),
            "client/new-name.ts",
        )

    def test_area_for_path_groups_major_roots(self) -> None:
        """Collapse important repo paths into stable business areas."""

        self.assertEqual(crw.area_for_path("client/app/page.tsx"), "client/app")
        self.assertEqual(
            crw.area_for_path("openspec/specs/auth/spec.md"),
            "openspec/specs",
        )
        self.assertEqual(
            crw.area_for_path(".github/workflows/test.yml"),
            ".github/workflows",
        )
        self.assertEqual(crw.area_for_path("README.md"), "README.md")

    def test_commit_matches_identity_by_email(self) -> None:
        """Match commits against the configured git email."""

        identity = crw.IdentityContext(
            git_user_name="Francisco",
            git_user_email="you@example.com",
            github_login="your-github-user",
            author_filter=None,
        )
        commit = {
            "author_name": "Another Name",
            "author_email": "you@example.com",
        }
        self.assertTrue(crw.commit_matches_identity(commit, identity))

    def test_truncate_text_collapses_whitespace(self) -> None:
        """Return a compact single-line excerpt."""

        text = "Line one.\n\nLine    two."
        self.assertEqual(crw.truncate_text(text, 50), "Line one. Line two.")


if __name__ == "__main__":
    unittest.main()
