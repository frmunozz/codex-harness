#!/usr/bin/env python3
"""Portable Codex config backup, install, sync, and rollback tool."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
BACKUP_ROOT = PACKAGE_ROOT / "backup"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
AGENTS_HOME = Path(os.environ.get("AGENTS_HOME", Path.home() / ".agents")).expanduser()

# scope, target-relative path, package-relative source path
MANAGED: Tuple[Tuple[str, Path, Path], ...] = (
    ("codex", Path("AGENTS.md"), Path("instructions/AGENTS.md")),
    ("codex", Path("agents"), Path("agents")),
    ("codex", Path("hooks"), Path("hooks")),
)

REMOVE: Tuple[Tuple[str, Path, str], ...] = (
    ("codex", Path("hooks.json"), "file"),
)

# Backed up and restorable, but never copied from the package during install.
BACKUP_ONLY: Tuple[Tuple[str, Path, str], ...] = (
    ("agents", Path("skills"), "directory"),
    ("codex", Path("skills"), "directory"),
    ("agents", Path(".skill-lock.json"), "file"),
)


def root_for(scope: str) -> Path:
    return CODEX_HOME if scope == "codex" else AGENTS_HOME


def source_files(source: Path) -> Iterable[Tuple[Path, Path]]:
    """Yield package-relative source path and absolute source path."""
    if source.is_file():
        yield source.relative_to(PACKAGE_ROOT), source
        return
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        yield path.relative_to(PACKAGE_ROOT), path


def managed_files() -> Iterable[Tuple[str, Path, Path, Path]]:
    for scope, target_root, source_root in MANAGED:
        source = PACKAGE_ROOT / source_root
        if not source.exists():
            raise RuntimeError(f"Missing package source: {source}")
        if source.is_file():
            yield scope, target_root, source, source
            continue
        for _, path in source_files(source):
            yield scope, target_root / path.relative_to(source), path, source


def backup_targets() -> Iterable[Tuple[str, Path, str]]:
    for scope, relative, source in MANAGED:
        yield scope, relative, "directory" if (PACKAGE_ROOT / source).is_dir() else "file"
    yield "codex", Path("config.toml"), "file"
    yield from REMOVE
    yield from BACKUP_ONLY


def target_path(scope: str, relative: Path) -> Path:
    return root_for(scope) / relative


def ensure_safe_roots() -> None:
    package = PACKAGE_ROOT.resolve()
    for name, root in (("CODEX_HOME", CODEX_HOME), ("AGENTS_HOME", AGENTS_HOME)):
        resolved = root.resolve()
        if resolved == package or package in resolved.parents:
            raise RuntimeError(
                f"Refusing to install into {name} inside the harness repository: {resolved}"
            )


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def copy_path(source: Path, destination: Path) -> None:
    """Copy a file/tree while preserving symlinks used by skills."""
    if source.is_symlink():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(os.readlink(source), target_is_directory=source.is_dir())
    elif source.is_dir():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, symlinks=True)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=False)


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def new_backup_dir() -> Path:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
    base = BACKUP_ROOT / timestamp()
    candidate = base
    suffix = 1
    while candidate.exists():
        candidate = BACKUP_ROOT / f"{base.name}-{suffix}"
        suffix += 1
    candidate.mkdir()
    return candidate


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def create_backup() -> Path:
    ensure_safe_roots()
    backup = new_backup_dir()
    entries: List[Dict[str, object]] = []

    for scope, relative, expected_kind in backup_targets():
        target = target_path(scope, relative)
        exists = path_exists(target)
        if exists:
            kind = "directory" if target.is_dir() else "file"
            if kind != expected_kind and (scope, relative, expected_kind) not in REMOVE:
                raise RuntimeError(f"Unexpected target type for {target}: expected {expected_kind}")
        else:
            kind = expected_kind
        entry: Dict[str, object] = {
            "scope": scope,
            "path": relative.as_posix(),
            "existed": exists,
            "kind": kind,
        }
        if exists:
            saved = backup / scope / relative
            copy_path(target, saved)
        elif kind == "directory":
            (backup / scope / relative).mkdir(parents=True, exist_ok=True)
        entries.append(entry)

    write_json(
        backup / "manifest.json",
        {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "codex_home": str(CODEX_HOME),
            "agents_home": str(AGENTS_HOME),
            "entries": entries,
        },
    )
    return backup


def copy_package_to_targets() -> int:
    count = 0
    for scope, relative, source, _ in managed_files():
        target = target_path(scope, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        count += 1
    return count


def remove_target(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)
    elif path_exists(target):
        raise RuntimeError(f"Refusing to remove unsupported target: {target}")


def remove_install_targets() -> int:
    removed = 0
    for scope, relative, source in MANAGED:
        if (PACKAGE_ROOT / source).is_dir():
            target = target_path(scope, relative)
            if target.exists():
                remove_target(target)
                removed += 1
    for scope, relative, _ in REMOVE:
        target = target_path(scope, relative)
        if target.exists():
            remove_target(target)
            removed += 1
    return removed


def sync_targets_to_package() -> int:
    count = 0
    for scope, relative, source_root in MANAGED:
        target = target_path(scope, relative)
        source = PACKAGE_ROOT / source_root
        if source.is_file():
            if not target.is_file():
                raise RuntimeError(f"Missing local managed file: {target}")
            shutil.copy2(target, source)
            count += 1
            continue

        if not target.is_dir():
            raise RuntimeError(f"Missing local managed directory: {target}")
        source.mkdir(parents=True, exist_ok=True)
        target_files = [
            path
            for path in sorted(target.rglob("*"))
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
        ]
        target_relative = {path.relative_to(target) for path in target_files}
        for path in target_files:
            destination = source / path.relative_to(target)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            count += 1
        for path in sorted(source.rglob("*"), reverse=True):
            if path.is_file() and path.relative_to(source) not in target_relative:
                path.unlink()
                count += 1
    return count


def confirm(prompt: str, yes: bool) -> None:
    if yes:
        return
    if not sys.stdin.isatty():
        raise RuntimeError("Non-interactive install/rollback requires --yes")
    if input(f"{prompt} Type 'yes' to continue: ").strip().lower() != "yes":
        raise RuntimeError("Cancelled")


def backup_id_from_arg(value: str) -> Path:
    if Path(value).name != value or Path(value).is_absolute():
        raise RuntimeError(f"Invalid backup ID: {value}")
    path = BACKUP_ROOT / value
    if not path.is_dir():
        raise RuntimeError(f"Backup not found: {path}")
    return path


def read_manifest(backup: Path) -> List[Dict[str, object]]:
    manifest_path = backup / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Invalid backup: {manifest_path} missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return list(manifest.get("entries", []))


def rollback(backup: Path) -> int:
    restored = 0
    for entry in read_manifest(backup):
        scope = str(entry["scope"])
        relative = Path(str(entry["path"]))
        target = target_path(scope, relative)
        saved = backup / scope / relative
        if entry.get("existed"):
            if not path_exists(saved):
                raise RuntimeError(f"Backup entry missing: {saved}")
            remove_target(target)
            copy_path(saved, target)
        elif path_exists(target):
            remove_target(target)
        restored += 1
    return restored


def cmd_status(_: argparse.Namespace) -> None:
    package_files = sum(1 for _ in managed_files())
    print(f"package: {PACKAGE_ROOT}")
    print(f"CODEX_HOME: {CODEX_HOME} ({'exists' if CODEX_HOME.exists() else 'missing'})")
    print(f"AGENTS_HOME: {AGENTS_HOME} ({'exists' if AGENTS_HOME.exists() else 'missing'})")
    print(f"managed files: {package_files}")
    if BACKUP_ROOT.exists():
        backups = sorted((p.name for p in BACKUP_ROOT.iterdir() if p.is_dir()), reverse=True)
        print(f"backups: {', '.join(backups) if backups else 'none'}")
    else:
        print("backups: none")


def cmd_backup(_: argparse.Namespace) -> None:
    backup = create_backup()
    print(f"backup: {backup.name}")
    print(f"path: {backup}")


def cmd_install(args: argparse.Namespace) -> None:
    ensure_safe_roots()
    if args.dry_run:
        for scope, relative, source, _ in managed_files():
            print(f"{target_path(scope, relative)} <= {source}")
        for scope, relative, _ in BACKUP_ONLY:
            if path_exists(target_path(scope, relative)):
                print(f"BACKUP {target_path(scope, relative)}")
        for scope, relative, source in MANAGED:
            if (PACKAGE_ROOT / source).is_dir() and target_path(scope, relative).exists():
                print(f"REPLACE {target_path(scope, relative)}")
        for scope, relative, _ in REMOVE:
            if target_path(scope, relative).exists():
                print(f"REMOVE {target_path(scope, relative)}")
        return
    confirm(
        f"Install {PACKAGE_ROOT.name} into {CODEX_HOME} and {AGENTS_HOME}?",
        args.yes,
    )
    backup = create_backup()
    removed = remove_install_targets()
    count = copy_package_to_targets()
    print(f"backup: {backup.name}")
    print(f"installed files: {count}")
    print(f"replaced/removed paths: {removed}")


def cmd_list_backups(_: argparse.Namespace) -> None:
    if not BACKUP_ROOT.exists():
        print("no backups")
        return
    for path in sorted((p for p in BACKUP_ROOT.iterdir() if p.is_dir()), reverse=True):
        print(path.name)


def cmd_rollback(args: argparse.Namespace) -> None:
    ensure_safe_roots()
    backup = backup_id_from_arg(args.backup_id)
    if args.dry_run:
        print(f"would rollback: {backup.name}")
        for entry in read_manifest(backup):
            target = target_path(str(entry["scope"]), Path(str(entry["path"])))
            action = "RESTORE" if entry.get("existed") else "REMOVE"
            print(f"{action} {target}")
        return
    confirm(f"Rollback {backup.name}?", args.yes)
    count = rollback(backup)
    print(f"rolled back entries: {count}")


def cmd_sync(args: argparse.Namespace) -> None:
    ensure_safe_roots()
    if args.dry_run:
        for scope, relative, source_root in MANAGED:
            target = target_path(scope, relative)
            source = PACKAGE_ROOT / source_root
            if source.is_file():
                print(f"{source} <= {target}")
                continue
            if not target.is_dir():
                print(f"MISSING {target}")
                continue
            target_files = {
                path.relative_to(target)
                for path in target.rglob("*")
                if path.is_file()
                and ".git" not in path.parts
                and "__pycache__" not in path.parts
            }
            for relative_path in sorted(target_files):
                print(f"{source / relative_path} <= {target / relative_path}")
            for path in sorted(source.rglob("*")):
                if path.is_file() and path.relative_to(source) not in target_files:
                    print(f"REMOVE {path}")
        return
    confirm(
        f"Sync current setup from {CODEX_HOME} and {AGENTS_HOME} into {PACKAGE_ROOT.name}?",
        args.yes,
    )
    count = sync_targets_to_package()
    print(f"synced files: {count}")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)

    commands.add_parser("status").set_defaults(handler=cmd_status)
    commands.add_parser("backup").set_defaults(handler=cmd_backup)
    commands.add_parser("list-backups").set_defaults(handler=cmd_list_backups)

    install = commands.add_parser("install")
    install.add_argument("--yes", action="store_true")
    install.add_argument("--dry-run", action="store_true")
    install.set_defaults(handler=cmd_install)

    rollback_cmd = commands.add_parser("rollback")
    rollback_cmd.add_argument("backup_id")
    rollback_cmd.add_argument("--yes", action="store_true")
    rollback_cmd.add_argument("--dry-run", action="store_true")
    rollback_cmd.set_defaults(handler=cmd_rollback)

    sync = commands.add_parser("sync")
    sync.add_argument("--yes", action="store_true")
    sync.add_argument("--dry-run", action="store_true")
    sync.set_defaults(handler=cmd_sync)
    return root


def main() -> int:
    try:
        args = parser().parse_args()
        args.handler(args)
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
