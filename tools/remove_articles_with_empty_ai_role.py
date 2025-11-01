#!/usr/bin/env python3
"""
Backup and remove article blocks where the '**AI Role:**' field is empty.

Behavior:
 - Treat an article as the text starting at a line beginning with '## ' up to (but not including) the next '## ' or EOF.
 - Inside each article, find the line that starts with '**AI Role:**'. If that line has no content after the colon and
   there is no following non-empty paragraph (before the next field starting with '**' or a heading), consider it empty.
 - Remove the entire article block if AI Role is empty. Create a backup with suffix '.bak3'.
"""
from pathlib import Path
import shutil
import re


def is_ai_role_empty(block_lines):
    # Find the AI Role line
    for idx, line in enumerate(block_lines):
        if line.lstrip().startswith("**AI Role:**"):
            # Check same-line content after colon
            after = line.split("**AI Role:**", 1)[1]
            if after.strip():
                return False
            # look ahead for next non-empty, non-field line
            j = idx + 1
            while j < len(block_lines):
                nxt = block_lines[j].rstrip("\n")
                if nxt.strip() == "":
                    j += 1
                    continue
                # if next non-empty starts with '**' or '##' or '###' -> it's a field/heading not content
                if nxt.lstrip().startswith("**") or nxt.lstrip().startswith("##") or nxt.lstrip().startswith("###"):
                    return True
                # otherwise it's content text -> not empty
                return False
            # reached end without finding content
            return True
    # if no AI Role field found, treat as non-empty (do not delete)
    return False


def main():
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "data" / "medrxiv-ai-20251101-102613.md"
    if not target.exists():
        print(f"Target file not found: {target}")
        return

    backup = target.with_suffix(target.suffix + ".bak3")
    shutil.copy2(target, backup)
    print(f"Backup written to: {backup}")

    text = target.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    articles = []  # list of (start_idx, end_idx) for article blocks
    current_start = None
    for i, line in enumerate(lines):
        if line.startswith("## "):
            if current_start is not None:
                articles.append((current_start, i))
            current_start = i
    if current_start is not None:
        articles.append((current_start, len(lines)))

    to_keep = []
    removed_count = 0
    last = 0
    for (s, e) in articles:
        # append content before this article
        if last < s:
            to_keep.extend(lines[last:s])
        block = lines[s:e]
        if is_ai_role_empty(block):
            removed_count += 1
            # skip this block (do not add to to_keep)
        else:
            to_keep.extend(block)
        last = e

    # append any trailing content after last article
    if last < len(lines):
        to_keep.extend(lines[last:])

    target.write_text(''.join(to_keep), encoding="utf-8")
    print(f"Removed {removed_count} articles with empty '**AI Role:**'")


if __name__ == "__main__":
    main()
