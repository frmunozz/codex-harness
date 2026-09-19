"""Optional cross-platform RTK guard for Codex hook runners."""

import json
import os
import shlex
import shutil
import sys


def _rtk_executable() -> str | None:
    configured = os.environ.get("RTK_EXE")
    if configured:
        return configured
    return shutil.which("rtk") or shutil.which("rtk.exe")


def _first_token(command: str) -> str:
    try:
        return shlex.split(command, posix=os.name != "nt")[0]
    except (IndexError, ValueError):
        return command.split(maxsplit=1)[0]


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return

    command = ((payload.get("tool_input") or {}).get("command") or "").strip()
    if not command:
        return

    rtk = _rtk_executable()
    if not rtk:
        return

    if _first_token(command).strip("\"'").casefold() == rtk.casefold():
        return

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Prefix shell commands with {rtk}. "
                        f"Suggested command: {rtk} {command}"
                    ),
                }
            }
        )
    )


if __name__ == "__main__":
    main()
