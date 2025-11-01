#!/usr/bin/env python3
"""
Backup and remove occurrences of '### Abstract (excerpt)' and the following paragraph
from the specified markdown file.

Behavior:
 - Create a backup at the same path with suffix `.bak`.
 - For each line that starts with '### Abstract (excerpt)', remove that line and
   then remove the subsequent consecutive non-empty lines (the immediate paragraph)
   up to the next blank line. Leave the blank line for spacing.
"""
from pathlib import Path
import shutil


def process_file(target: Path) -> int:
    with target.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # First pass: remove headings and their immediate paragraph(s)
    new_lines = []
    i = 0
    removed_blocks = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.lstrip().startswith("### Abstract (excerpt)"):
            # skip the heading
            i += 1
            # skip any immediate blank lines after the heading
            while i < n and lines[i].strip() == "":
                i += 1
            # skip following non-empty lines (the paragraph)
            while i < n and lines[i].strip() != "":
                i += 1
            # keep one blank line if there is one (for readability)
            if i < n and lines[i].strip() == "":
                new_lines.append("\n")
                i += 1
            removed_blocks += 1
            continue
        else:
            new_lines.append(line)
            i += 1

    # Second pass: remove paragraph that immediately follows a '**Metrics:**' line
    lines2 = []
    i = 0
    n = len(new_lines)
    while i < n:
        line = new_lines[i]
        lines2.append(line)
        if line.lstrip().startswith("**Metrics:**"):
            # look ahead: skip blank lines
            j = i + 1
            while j < n and new_lines[j].strip() == "":
                j += 1
            # if the next non-empty line exists and does NOT start with a markdown field or heading,
            # treat it as the abstract paragraph and skip it
            if j < n:
                nxt = new_lines[j]
                if not (nxt.lstrip().startswith("**") or nxt.lstrip().startswith("##") or nxt.lstrip().startswith("###") or nxt.lstrip().startswith("---") or nxt.lstrip().startswith("URL:") or nxt.lstrip().startswith("**URL:")):
                    # remove the paragraph: skip consecutive non-empty lines starting at j
                    k = j
                    while k < n and new_lines[k].strip() != "":
                        k += 1
                    # ensure we leave one blank line for spacing
                    lines2.append("\n")
                    i = k
                    continue
        i += 1

    with target.open("w", encoding="utf-8") as f:
        f.writelines(lines2)

    return removed_blocks


def main():
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "data" / "medrxiv-ai-20251101-102613.md"
    if not target.exists():
        print(f"Target file not found: {target}")
        return

    backup = target.with_suffix(target.suffix + ".bak")
    shutil.copy2(target, backup)
    print(f"Backup written to: {backup}")

    removed = process_file(target)
    print(f"Removed {removed} '### Abstract (excerpt)' blocks from {target.name}")


if __name__ == "__main__":
    main()
