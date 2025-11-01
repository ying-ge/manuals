#!/usr/bin/env python3
"""
Renumber article headings in the medrxiv markdown file.

Find lines that start with '##' and an existing numeric prefix like '## 12.' and
replace the number with a sequential index starting at 1 in order of appearance.

Creates a backup with suffix '.renumber.bak'.
"""
from pathlib import Path
import shutil
import re


def renumber_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    count = 0
    changed = 0
    out = []
    header_re = re.compile(r'^(##\s*)(\d+)\.(\s*)')
    for line in lines:
        m = header_re.match(line)
        if m:
            count += 1
            prefix, oldnum, sep = m.group(1), m.group(2), m.group(3)
            new_line = f"{prefix}{count}.{sep}" + line[m.end():]
            out.append(new_line)
            if oldnum != str(count):
                changed += 1
        else:
            out.append(line)

    path.write_text(''.join(out), encoding="utf-8")
    return changed


def main():
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "data" / "medrxiv-ai-20251101-102613.md"
    if not target.exists():
        print(f"Target not found: {target}")
        return

    backup = target.with_suffix(target.suffix + ".renumber.bak")
    shutil.copy2(target, backup)
    print(f"Backup created: {backup}")

    changed = renumber_file(target)
    print(f"Renumbered headings; {changed} headings updated to sequential numbers")


if __name__ == '__main__':
    main()
