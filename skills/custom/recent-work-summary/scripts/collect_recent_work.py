#!/usr/bin/env python3
"""Collect recent git and GitHub activity for a business summary."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path, PurePosixPath
from shutil import which
from typing import Any, Iterable, Sequence


PR_FIELDS = (
    "number,title,state,isDraft,createdAt,updatedAt,mergedAt,"
    "additions,deletions,changedFiles,labels,closingIssuesReferences,url,body"
)
ISSUE_FIELDS = (
    "number,title,state,stateReason,createdAt,updatedAt,closedAt,"
    "labels,url,body"
)
SEARCH_PR_FIELDS = "number,title,state,updatedAt,url,createdAt,isDraft"
SEARCH_ISSUE_FIELDS = "number,title,state,updatedAt,url,createdAt,isPullRequest"
MAX_BODY_CHARS = 1200
MAX_STATUS_ENTRIES = 20


@dataclass(frozen=True)
class CommandResult:
    """Store shell command output."""

    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class IdentityContext:
    """Store the identity filters used to match work."""

    git_user_name: str | None
    git_user_email: str | None
    github_login: str | None
    author_filter: str | None


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Collect recent commits, diff stats, pull requests, and issues "
            "for a business-facing work summary."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path inside the target git repository.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Look back this many days from now.",
    )
    parser.add_argument(
        "--author",
        default=None,
        help="Optional git author override (name or email).",
    )
    parser.add_argument(
        "--github-user",
        default=None,
        help="Optional GitHub login override.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum PRs or issues to fetch per GitHub query.",
    )
    return parser.parse_args()


def main() -> int:
    """Collect recent work data and write it as JSON."""

    args = parse_args()
    repo_root = find_git_root(Path(args.repo))
    if repo_root is None:
        print("Error: not inside a git repository.", file=sys.stderr)
        return 1

    now_local = datetime.now().astimezone()
    since_local = now_local - timedelta(days=max(0, args.days))
    identity = resolve_identity(
        repo_root=repo_root,
        author_filter=args.author,
        github_user=args.github_user,
    )
    workspace = collect_workspace_state(repo_root)
    try:
        commits, git_warnings = collect_recent_commits(
            repo_root=repo_root,
            since_local=since_local,
            identity=identity,
        )
        git_summary = build_git_summary(commits)
        github_context = collect_github_context(
            repo_root=repo_root,
            since_date=since_local.date(),
            github_login=identity.github_login,
            limit=max(1, args.limit),
        )
        pending_items = collect_pending_items(workspace, github_context)
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    payload = {
        "generated_at": now_local.isoformat(),
        "repo_root": str(repo_root),
        "window": {
            "days": max(0, args.days),
            "since": since_local.isoformat(),
            "until": now_local.isoformat(),
        },
        "identity": {
            "git_user_name": identity.git_user_name,
            "git_user_email": identity.git_user_email,
            "github_login": identity.github_login,
            "author_filter": identity.author_filter,
        },
        "workspace": workspace,
        "git": git_summary,
        "github": github_context,
        "pending": pending_items,
        "warnings": git_warnings + github_context.get("warnings", []),
    }
    print(json.dumps(payload, indent=2))
    return 0


def find_git_root(start: Path) -> Path | None:
    """Return the repository root for the provided path."""

    result = run_command(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def resolve_identity(
    repo_root: Path,
    author_filter: str | None,
    github_user: str | None,
) -> IdentityContext:
    """Resolve git and GitHub identities for filtering recent work."""

    git_user_name = read_git_config(repo_root, "user.name")
    git_user_email = read_git_config(repo_root, "user.email")
    github_login = github_user or read_github_login(repo_root)
    return IdentityContext(
        git_user_name=git_user_name,
        git_user_email=git_user_email,
        github_login=github_login,
        author_filter=author_filter,
    )


def read_git_config(repo_root: Path, key: str) -> str | None:
    """Read a git configuration value."""

    result = run_command(["git", "config", key], cwd=repo_root)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def read_github_login(repo_root: Path) -> str | None:
    """Read the current GitHub login if gh is available and authenticated."""

    if which("gh") is None:
        return None

    auth_result = run_command(["gh", "auth", "status"], cwd=repo_root)
    if auth_result.returncode != 0:
        return None

    result = run_command(["gh", "api", "user"], cwd=repo_root)
    if result.returncode != 0:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    login = payload.get("login")
    if isinstance(login, str) and login.strip():
        return login.strip()
    return None


def collect_workspace_state(repo_root: Path) -> dict[str, Any]:
    """Collect local branch and workspace status details."""

    branch_result = run_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_root,
    )
    status_result = run_command(["git", "status", "--short"], cwd=repo_root)
    upstream_result = run_command(
        ["git", "rev-list", "--left-right", "--count", "@{upstream}...HEAD"],
        cwd=repo_root,
    )

    status_lines = [
        line
        for line in status_result.stdout.splitlines()
        if line.strip()
    ]
    ahead_count: int | None = None
    behind_count: int | None = None
    if upstream_result.returncode == 0:
        parts = upstream_result.stdout.strip().split()
        if len(parts) == 2:
            behind_count = int(parts[0])
            ahead_count = int(parts[1])

    return {
        "branch": branch_result.stdout.strip() or None,
        "has_uncommitted_changes": bool(status_lines),
        "uncommitted_entry_count": len(status_lines),
        "uncommitted_entries": status_lines[:MAX_STATUS_ENTRIES],
        "ahead_of_upstream": ahead_count,
        "behind_upstream": behind_count,
    }


def collect_recent_commits(
    repo_root: Path,
    since_local: datetime,
    identity: IdentityContext,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Collect recent commits that match the selected identity."""

    warnings: list[str] = []
    result = run_command(
        [
            "git",
            "log",
            "--all",
            f"--since={since_local.isoformat()}",
            "--date=iso-strict",
            "--format=%x1e%H%x1f%aI%x1f%an%x1f%ae%x1f%s%x1f%b",
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git log failed")

    commits: list[dict[str, Any]] = []
    fallback_all_authors = should_include_all_authors(identity)
    if fallback_all_authors:
        warnings.append(
            "No git author filter could be resolved, so all recent authors "
            "were included."
        )

    for raw_block in result.stdout.split("\x1e"):
        block = raw_block.strip()
        if not block:
            continue
        parts = block.split("\x1f", 5)
        if len(parts) < 5:
            continue
        sha = parts[0].strip()
        commit = {
            "sha": sha,
            "date": parts[1].strip(),
            "author_name": parts[2].strip(),
            "author_email": parts[3].strip(),
            "subject": parts[4].strip(),
            "body": parts[5].strip() if len(parts) > 5 else "",
        }
        if fallback_all_authors or commit_matches_identity(commit, identity):
            commits.append(build_commit_summary(repo_root, commit))

    return commits, warnings


def should_include_all_authors(identity: IdentityContext) -> bool:
    """Return whether commit filtering must fall back to all authors."""

    if identity.author_filter:
        return False
    return not any(
        [
            identity.git_user_name,
            identity.git_user_email,
            identity.github_login,
        ]
    )


def commit_matches_identity(
    commit: dict[str, Any],
    identity: IdentityContext,
) -> bool:
    """Return whether a commit belongs to the selected identity."""

    author_name = normalize_text(commit.get("author_name"))
    author_email = normalize_text(commit.get("author_email"))
    explicit = normalize_text(identity.author_filter)

    if explicit:
        if "@" in explicit:
            return explicit in author_email
        return explicit in author_name or explicit in author_email

    name_match = False
    email_match = False
    login_match = False

    if identity.git_user_name:
        name_match = author_name == normalize_text(identity.git_user_name)
    if identity.git_user_email:
        email_match = author_email == normalize_text(identity.git_user_email)
    if identity.github_login and not (name_match or email_match):
        login = normalize_text(identity.github_login)
        local_part = author_email.split("@", 1)[0]
        login_match = login in author_name or login == local_part

    return name_match or email_match or login_match


def build_commit_summary(
    repo_root: Path,
    commit: dict[str, Any],
) -> dict[str, Any]:
    """Build a commit summary with per-file diff stats."""

    files = collect_commit_files(repo_root, str(commit["sha"]))
    insertions = sum(file_entry["insertions"] for file_entry in files)
    deletions = sum(file_entry["deletions"] for file_entry in files)
    areas = sorted({file_entry["area"] for file_entry in files})

    return {
        "sha": commit["sha"],
        "short_sha": str(commit["sha"])[:7],
        "date": commit["date"],
        "author_name": commit["author_name"],
        "author_email": commit["author_email"],
        "subject": commit["subject"],
        "body_excerpt": truncate_text(str(commit["body"]), MAX_BODY_CHARS),
        "insertions": insertions,
        "deletions": deletions,
        "file_count": len(files),
        "areas": areas,
        "files": files,
    }


def collect_commit_files(repo_root: Path, sha: str) -> list[dict[str, Any]]:
    """Collect numstat output for a single commit."""

    result = run_command(
        [
            "git",
            "show",
            "--numstat",
            "--format=",
            "--find-renames",
            sha,
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git show failed for {sha}")

    files: list[dict[str, Any]] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        insertions = parse_numstat_value(parts[0])
        deletions = parse_numstat_value(parts[1])
        raw_path = parts[2].strip()
        path = normalize_git_path(raw_path)
        area = area_for_path(path)
        files.append(
            {
                "path": path,
                "insertions": insertions,
                "deletions": deletions,
                "changes": insertions + deletions,
                "area": area,
                "extension": file_extension(path),
            }
        )
    return files


def parse_numstat_value(value: str) -> int:
    """Parse a numstat insertion or deletion value."""

    if value == "-":
        return 0
    return int(value)


def normalize_git_path(raw_path: str) -> str:
    """Normalize git rename paths to the destination path."""

    if " => " not in raw_path:
        return raw_path

    if "{" in raw_path and "}" in raw_path:
        prefix, remainder = raw_path.split("{", 1)
        middle, suffix = remainder.split("}", 1)
        if " => " in middle:
            _, destination = middle.split(" => ", 1)
            return f"{prefix}{destination}{suffix}"

    return raw_path.split(" => ", 1)[1]


def area_for_path(path: str) -> str:
    """Return a stable area label for a repository path."""

    normalized = path.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    parts = PurePosixPath(normalized).parts
    if not parts:
        return "(root)"

    first = parts[0]
    if len(parts) == 1:
        return first

    second = parts[1]
    if "." in second:
        return first

    grouped_roots = {
        ".agents",
        ".codex",
        ".github",
        "backend",
        "client",
        "docs",
        "openspec",
        "windows-client",
    }
    if first in grouped_roots:
        return f"{first}/{second}"
    return first


def file_extension(path: str) -> str:
    """Return a lowercase file extension label."""

    suffix = PurePosixPath(path).suffix.lower()
    return suffix or "[none]"


def build_git_summary(commits: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate commit-level details into repository change statistics."""

    total_insertions = sum(commit["insertions"] for commit in commits)
    total_deletions = sum(commit["deletions"] for commit in commits)
    file_map: dict[str, dict[str, Any]] = {}
    area_map: dict[str, dict[str, Any]] = {}
    extension_map: dict[str, dict[str, Any]] = {}

    for commit in commits:
        for file_entry in commit["files"]:
            path = str(file_entry["path"])
            area = str(file_entry["area"])
            extension = str(file_entry["extension"])

            file_row = file_map.setdefault(
                path,
                {
                    "path": path,
                    "insertions": 0,
                    "deletions": 0,
                    "changes": 0,
                    "area": area,
                },
            )
            file_row["insertions"] += file_entry["insertions"]
            file_row["deletions"] += file_entry["deletions"]
            file_row["changes"] += file_entry["changes"]

            area_row = area_map.setdefault(
                area,
                {
                    "area": area,
                    "insertions": 0,
                    "deletions": 0,
                    "changes": 0,
                    "files_changed": set(),
                    "commits": set(),
                },
            )
            area_row["insertions"] += file_entry["insertions"]
            area_row["deletions"] += file_entry["deletions"]
            area_row["changes"] += file_entry["changes"]
            area_row["files_changed"].add(path)
            area_row["commits"].add(commit["sha"])

            extension_row = extension_map.setdefault(
                extension,
                {
                    "extension": extension,
                    "files_changed": set(),
                    "insertions": 0,
                    "deletions": 0,
                    "changes": 0,
                },
            )
            extension_row["files_changed"].add(path)
            extension_row["insertions"] += file_entry["insertions"]
            extension_row["deletions"] += file_entry["deletions"]
            extension_row["changes"] += file_entry["changes"]

    areas = []
    for area_row in area_map.values():
        areas.append(
            {
                "area": area_row["area"],
                "insertions": area_row["insertions"],
                "deletions": area_row["deletions"],
                "changes": area_row["changes"],
                "files_changed": len(area_row["files_changed"]),
                "commit_count": len(area_row["commits"]),
            }
        )

    file_types = []
    for extension_row in extension_map.values():
        file_types.append(
            {
                "extension": extension_row["extension"],
                "files_changed": len(extension_row["files_changed"]),
                "insertions": extension_row["insertions"],
                "deletions": extension_row["deletions"],
                "changes": extension_row["changes"],
            }
        )

    return {
        "commit_count": len(commits),
        "file_count": len(file_map),
        "insertions": total_insertions,
        "deletions": total_deletions,
        "net_lines": total_insertions - total_deletions,
        "commits": commits,
        "areas": sort_rows(areas, key="changes"),
        "top_files": sort_rows(file_map.values(), key="changes")[:10],
        "file_types": sort_rows(file_types, key="changes")[:10],
    }


def collect_github_context(
    repo_root: Path,
    since_date: date,
    github_login: str | None,
    limit: int,
) -> dict[str, Any]:
    """Collect recent PR and issue context from GitHub."""

    context: dict[str, Any] = {
        "available": False,
        "repo": None,
        "user_login": github_login,
        "authored_prs": [],
        "involved_prs": [],
        "authored_issues": [],
        "involved_issues": [],
        "warnings": [],
    }

    if which("gh") is None:
        context["warnings"].append("gh CLI is not installed.")
        return context

    auth_result = run_command(["gh", "auth", "status"], cwd=repo_root)
    if auth_result.returncode != 0:
        context["warnings"].append(
            "gh auth status failed, so PR and issue history was skipped."
        )
        return context

    repo_slug = read_repo_slug(repo_root)
    if repo_slug is None:
        context["warnings"].append(
            "Unable to resolve the GitHub repository slug."
        )
        return context

    login = github_login or read_github_login(repo_root)
    if not login:
        context["warnings"].append(
            "Unable to resolve the GitHub login for recent activity."
        )
        return context

    context["repo"] = repo_slug
    context["user_login"] = login
    since_filter = f">={since_date.isoformat()}"

    authored_prs = search_pull_requests(
        repo_root=repo_root,
        repo_slug=repo_slug,
        since_filter=since_filter,
        author=login,
        limit=limit,
    )
    authored_pr_numbers = {item["number"] for item in authored_prs}
    involved_prs = search_pull_requests(
        repo_root=repo_root,
        repo_slug=repo_slug,
        since_filter=since_filter,
        involves=login,
        limit=limit,
        exclude_numbers=authored_pr_numbers,
    )
    authored_issues = search_issues(
        repo_root=repo_root,
        repo_slug=repo_slug,
        since_filter=since_filter,
        author=login,
        limit=limit,
    )
    authored_issue_numbers = {item["number"] for item in authored_issues}
    involved_issues = search_issues(
        repo_root=repo_root,
        repo_slug=repo_slug,
        since_filter=since_filter,
        involves=login,
        limit=limit,
        exclude_numbers=authored_issue_numbers,
    )

    context["available"] = True
    context["authored_prs"] = authored_prs
    context["involved_prs"] = involved_prs
    context["authored_issues"] = authored_issues
    context["involved_issues"] = involved_issues

    for bucket_name in (
        "authored_prs",
        "involved_prs",
        "authored_issues",
        "involved_issues",
    ):
        bucket = context[bucket_name]
        if len(bucket) >= limit:
            context["warnings"].append(
                f"{bucket_name} reached the query limit of {limit} items."
            )

    return context


def read_repo_slug(repo_root: Path) -> str | None:
    """Read the current repository slug through gh."""

    result = run_command(
        ["gh", "repo", "view", "--json", "nameWithOwner"],
        cwd=repo_root,
    )
    if result.returncode != 0:
        return None
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    value = payload.get("nameWithOwner")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def search_pull_requests(
    repo_root: Path,
    repo_slug: str,
    since_filter: str,
    limit: int,
    author: str | None = None,
    involves: str | None = None,
    exclude_numbers: Iterable[int] = (),
) -> list[dict[str, Any]]:
    """Search recent pull requests and fetch detailed metadata."""

    args = [
        "gh",
        "search",
        "prs",
        "--repo",
        repo_slug,
        "--updated",
        since_filter,
        "--sort",
        "updated",
        "--order",
        "desc",
        "--limit",
        str(limit),
        "--json",
        SEARCH_PR_FIELDS,
    ]
    if author:
        args.extend(["--author", author])
    if involves:
        args.extend(["--involves", involves])

    result = run_command(args, cwd=repo_root)
    if result.returncode != 0:
        return []

    try:
        rows = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []

    excluded = set(exclude_numbers)
    detailed_items: list[dict[str, Any]] = []
    for row in rows:
        number = row.get("number")
        if not isinstance(number, int) or number in excluded:
            continue
        detail = fetch_pull_request_detail(repo_root, repo_slug, number)
        if detail is not None:
            detailed_items.append(detail)
    return detailed_items


def fetch_pull_request_detail(
    repo_root: Path,
    repo_slug: str,
    number: int,
) -> dict[str, Any] | None:
    """Fetch detailed metadata for a pull request."""

    result = run_command(
        [
            "gh",
            "pr",
            "view",
            str(number),
            "--repo",
            repo_slug,
            "--json",
            PR_FIELDS,
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        return None

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return None

    return {
        "number": payload.get("number"),
        "title": payload.get("title"),
        "state": payload.get("state"),
        "is_draft": payload.get("isDraft", False),
        "created_at": payload.get("createdAt"),
        "updated_at": payload.get("updatedAt"),
        "merged_at": payload.get("mergedAt"),
        "additions": payload.get("additions", 0),
        "deletions": payload.get("deletions", 0),
        "changed_files": payload.get("changedFiles", 0),
        "labels": label_names(payload.get("labels", [])),
        "closing_issues": closing_issue_refs(
            payload.get("closingIssuesReferences", [])
        ),
        "url": payload.get("url"),
        "body_excerpt": truncate_text(payload.get("body", ""), MAX_BODY_CHARS),
    }


def search_issues(
    repo_root: Path,
    repo_slug: str,
    since_filter: str,
    limit: int,
    author: str | None = None,
    involves: str | None = None,
    exclude_numbers: Iterable[int] = (),
) -> list[dict[str, Any]]:
    """Search recent issues and fetch detailed metadata."""

    args = [
        "gh",
        "search",
        "issues",
        "--repo",
        repo_slug,
        "--updated",
        since_filter,
        "--sort",
        "updated",
        "--order",
        "desc",
        "--limit",
        str(limit),
        "--json",
        SEARCH_ISSUE_FIELDS,
    ]
    if author:
        args.extend(["--author", author])
    if involves:
        args.extend(["--involves", involves])

    result = run_command(args, cwd=repo_root)
    if result.returncode != 0:
        return []

    try:
        rows = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        return []

    excluded = set(exclude_numbers)
    detailed_items: list[dict[str, Any]] = []
    for row in rows:
        if row.get("isPullRequest"):
            continue
        number = row.get("number")
        if not isinstance(number, int) or number in excluded:
            continue
        detail = fetch_issue_detail(repo_root, repo_slug, number)
        if detail is not None:
            detailed_items.append(detail)
    return detailed_items


def fetch_issue_detail(
    repo_root: Path,
    repo_slug: str,
    number: int,
) -> dict[str, Any] | None:
    """Fetch detailed metadata for an issue."""

    result = run_command(
        [
            "gh",
            "issue",
            "view",
            str(number),
            "--repo",
            repo_slug,
            "--json",
            ISSUE_FIELDS,
        ],
        cwd=repo_root,
    )
    if result.returncode != 0:
        return None

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return None

    return {
        "number": payload.get("number"),
        "title": payload.get("title"),
        "state": payload.get("state"),
        "state_reason": payload.get("stateReason"),
        "created_at": payload.get("createdAt"),
        "updated_at": payload.get("updatedAt"),
        "closed_at": payload.get("closedAt"),
        "labels": label_names(payload.get("labels", [])),
        "url": payload.get("url"),
        "body_excerpt": truncate_text(payload.get("body", ""), MAX_BODY_CHARS),
    }


def label_names(labels: Iterable[dict[str, Any]]) -> list[str]:
    """Extract label names from GitHub CLI JSON."""

    names: list[str] = []
    for label in labels:
        name = label.get("name")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return names


def closing_issue_refs(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize closing issue references from pull request JSON."""

    rows: list[dict[str, Any]] = []
    for item in items:
        rows.append(
            {
                "number": item.get("number"),
                "title": item.get("title"),
                "url": item.get("url"),
            }
        )
    return rows


def collect_pending_items(
    workspace: dict[str, Any],
    github_context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Collect likely pending items from local and GitHub state."""

    pending: list[dict[str, Any]] = []

    if workspace.get("has_uncommitted_changes"):
        pending.append(
            {
                "type": "local-uncommitted-changes",
                "title": "Local workspace has uncommitted changes",
                "reason": (
                    f"{workspace.get('uncommitted_entry_count', 0)} status "
                    "entries remain in the working tree."
                ),
            }
        )

    ahead = workspace.get("ahead_of_upstream")
    if isinstance(ahead, int) and ahead > 0:
        pending.append(
            {
                "type": "local-ahead-of-upstream",
                "title": "Local branch is ahead of upstream",
                "reason": f"{ahead} commit(s) have not reached upstream yet.",
            }
        )

    for pr in github_context.get("authored_prs", []):
        if pr.get("state") == "OPEN" or pr.get("is_draft"):
            pending.append(
                {
                    "type": "authored-pr",
                    "title": pr.get("title"),
                    "url": pr.get("url"),
                    "reason": "Authored pull request is still open or draft.",
                }
            )

    for pr in github_context.get("involved_prs", []):
        if pr.get("state") == "OPEN" or pr.get("is_draft"):
            pending.append(
                {
                    "type": "involved-pr",
                    "title": pr.get("title"),
                    "url": pr.get("url"),
                    "reason": (
                        "A pull request you were involved in is still open "
                        "or draft."
                    ),
                }
            )

    for issue in github_context.get("authored_issues", []):
        if issue.get("state") == "OPEN":
            pending.append(
                {
                    "type": "authored-issue",
                    "title": issue.get("title"),
                    "url": issue.get("url"),
                    "reason": "Authored issue is still open.",
                }
            )

    for issue in github_context.get("involved_issues", []):
        if issue.get("state") == "OPEN":
            pending.append(
                {
                    "type": "involved-issue",
                    "title": issue.get("title"),
                    "url": issue.get("url"),
                    "reason": "An issue you were involved in is still open.",
                }
            )

    return pending


def truncate_text(text: str | None, max_chars: int) -> str:
    """Collapse whitespace and truncate long bodies."""

    normalized = " ".join((text or "").split())
    if len(normalized) <= max_chars:
        return normalized
    return f"{normalized[: max_chars - 3].rstrip()}..."


def normalize_text(value: Any) -> str:
    """Normalize user-provided text for case-insensitive comparisons."""

    return str(value or "").strip().lower()


def sort_rows(
    rows: Iterable[dict[str, Any]],
    key: str,
) -> list[dict[str, Any]]:
    """Sort rows descending by the provided numeric key."""

    return sorted(rows, key=lambda row: row.get(key, 0), reverse=True)


def run_command(args: Sequence[str], cwd: Path) -> CommandResult:
    """Run a subprocess command and capture its output."""

    process = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    return CommandResult(
        returncode=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
    )


if __name__ == "__main__":
    raise SystemExit(main())
