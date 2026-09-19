"""Optional portable SessionStart hook."""

import json
import os
import sys
from pathlib import Path


def main() -> None:
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    agents_home = Path(os.environ.get("AGENTS_HOME", Path.home() / ".agents")).expanduser()
    paths = [
        agents_home / "skills" / "explore-delegation" / "SKILL.md",
        codex_home / "RTK.md",
        codex_home / "CAVEMAN_ULTRA.md",
    ]
    context = [p.read_text(encoding="utf-8").strip() for p in paths if p.is_file()]
    output = {"hookEventName": "SessionStart"}
    if context:
        output["additionalContext"] = "\n\n---\n\n".join(context)
    print(json.dumps({"continue": True, "hookSpecificOutput": output}))


if __name__ == "__main__":
    main()
