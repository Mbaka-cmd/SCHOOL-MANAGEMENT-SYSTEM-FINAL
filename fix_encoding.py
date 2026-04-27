"""
Run this script from your project root to fix the â€" encoding bug in all templates.

Usage:
    python fix_encoding.py
"""

import os
import re

TEMPLATES_DIR = "templates"
REPLACEMENTS = {
    "â€”": "—",
    "â€˜": "'",
    "â€™": "'",
    "â€œ": '"',
    "â€": '"',
    "â€¦": "…",
    "Â ": " ",
    "Â": "",
}

fixed_files = 0
fixed_count = 0

for root, dirs, files in os.walk(TEMPLATES_DIR):
    for filename in files:
        if filename.endswith(".html"):
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                original = content
                for bad, good in REPLACEMENTS.items():
                    content = content.replace(bad, good)

                if content != original:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    count = sum(
                        original.count(bad) for bad in REPLACEMENTS
                    )
                    print(f"  Fixed: {filepath}")
                    fixed_files += 1
                    fixed_count += count

            except Exception as e:
                print(f"  Error reading {filepath}: {e}")

print(f"\nDone! Fixed {fixed_count} encoding issues across {fixed_files} files.")