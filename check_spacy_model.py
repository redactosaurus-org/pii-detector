"""
Check if spaCy en_core_web_md model is installed
Returns 0 if installed, 1 if not installed
"""

import sys
import traceback

log_path = sys.argv[1] if len(sys.argv) > 1 else None


def write_log(message):
    if not log_path:
        return
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception:
        pass

try:
    import spacy
    # Try to load the model
    spacy.load("en_core_web_md")
except Exception as exc:
    write_log("ERROR: " + repr(exc))
    write_log(traceback.format_exc())
    print("not_installed")
    sys.exit(1)

write_log("installed")
print("installed")
sys.exit(0)
