"""
Rewrites JSON files so Unicode escape sequences (ú, é, etc.)
are replaced with their actual UTF-8 characters.

Usage:
    python fix_json.py                  # fixes all JSON files in output/
    python fix_json.py path/to/file.json
"""

import json
import sys
from pathlib import Path


def fix_file(path: Path):
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    fixed = json.dumps(data, ensure_ascii=False, indent=2)
    if fixed != text:
        path.write_text(fixed, encoding="utf-8")
        print(f"Fixed: {path}")
    else:
        print(f"Already clean: {path}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = [Path(p) for p in sys.argv[1:]]
    else:
        targets = list(Path("output").glob("*.json"))

    if not targets:
        print("No JSON files found.")
    else:
        for path in targets:
            fix_file(path)
