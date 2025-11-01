#!/usr/bin/env python3
"""
Backup and remove lines starting with "**All Affiliations:**" from the target markdown file.

Usage: run from repository root (script uses relative path to data file).
"""
import shutil
from pathlib import Path


def main():
    # script is in <repo>/tools/, so parents[1] is repo root
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "data" / "medrxiv-ai-20251101-102613.md"
    if not target.exists():
        print(f"Target file not found: {target}")
        return

    backup = target.with_suffix(target.suffix + ".bak")
    shutil.copy2(target, backup)
    print(f"Backup written to: {backup}")

    with target.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    removed_count = 0
    for line in lines:
        # strip left whitespace then check
        if line.lstrip().startswith("**All Affiliations:**"):
            removed_count += 1
            continue
        new_lines.append(line)

    with target.open("w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Removed {removed_count} lines starting with '**All Affiliations:**' from {target.name}")


if __name__ == "__main__":
    main()
