PATCH_ID = "2.1.0"
DESCRIPTION = "Initial modular patch framework"

def apply(app_text):
    changes = []

    old = "from datetime import datetime, timedelta, timedelta"
    new = "from datetime import datetime, timedelta"

    if old in app_text:
        app_text = app_text.replace(old, new)
        changes.append("Removed duplicate timedelta import")

    import_line = "from prompt_engine import build_prompt"

    if import_line not in app_text:
        marker = "from functools import wraps"

        if marker in app_text:
            app_text = app_text.replace(
                marker,
                marker + "\n" + import_line,
                1
            )
            changes.append("Added build_prompt import")

    return app_text, changes
