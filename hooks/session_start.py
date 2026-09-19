"""Optional portable SessionStart hook."""

import json


print(
    json.dumps(
        {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    "For open-ended exploration, source discovery, cross-file tracing, "
                    "or document/web surveying, use $explore-delegation. "
                    "Skip it for already-scoped tasks."
                ),
            },
        }
    )
)
