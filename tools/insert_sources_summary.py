#!/usr/bin/env python3
"""Insert or update a Sources summary block near the top of the medrxiv report.

Behavior:
- create a backup at the same path with suffix .insert.bak
- compute counts of `**Source:** <value>` occurrences
- insert a small summary block immediately after the first '---' metadata divider
- if a block starting with '## Sources summary' already exists at the top, replace it
"""
from collections import Counter
from datetime import datetime
import re
from pathlib import Path


def compute_source_counts(lines):
    src_re = re.compile(r"^\*\*Source:\*\*\s*(\S+)", re.IGNORECASE)
    counts = Counter()
    for ln in lines:
        m = src_re.match(ln.strip())
        if m:
            counts[m.group(1).lower()] += 1
    return counts


def build_summary_block(total, counts):
    # Keep consistent english headings with a short one-line explanation
    lines = []
    lines.append("## Sources summary")
    lines.append("")
    lines.append(f"**Total Articles (detected):** {total}")
    lines.append("")
    lines.append("**Source distribution:**")
    for k, v in counts.most_common():
        pct = (v / total * 100) if total else 0
        lines.append(f"- {k}: {v} ({pct:.1f}%)")
    lines.append("")
    lines.append("---")
    lines.append("")
    return [l + "\n" for l in lines]


def main():
    repo = Path(__file__).resolve().parents[1]
    data_file = repo / "data" / "medrxiv-ai-20251101-102613.md"
    if not data_file.exists():
        print(f"Data file not found: {data_file}")
        return 2

    text = data_file.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    # make a safe backup with timestamp
    bak = data_file.with_suffix(data_file.suffix + ".insert.bak")
    bak.write_bytes(data_file.read_bytes())
    print(f"Backup created: {bak}")

    counts = compute_source_counts(lines)
    # fallback total: count headings starting with '## ' after modifications
    total_headings = sum(1 for ln in lines if ln.startswith("## "))
    total = total_headings
    summary_block = build_summary_block(total, counts)

    # Find first '---' divider to insert after it. If not found, insert at top.
    insert_idx = None
    for i, ln in enumerate(lines[:50]):
        if ln.strip() == "---":
            insert_idx = i + 1
            break

    if insert_idx is None:
        insert_idx = 0

    # If there is an existing '## Sources summary' near the top (first 80 lines), remove that block first
    start = None
    for i, ln in enumerate(lines[:80]):
        if ln.strip().lower().startswith("## sources summary"):
            start = i
            break
    end = None
    if start is not None:
        # find the next '---' after start or next top-level heading '## '
        for j in range(start + 1, len(lines)):
            if lines[j].strip() == '---' or lines[j].startswith('## '):
                end = j
                break
        if end is None:
            end = start + 1

        # replace existing block
        new_lines = lines[:start] + summary_block + lines[end:]
    else:
        new_lines = lines[:insert_idx] + summary_block + lines[insert_idx:]

    data_file.write_text(''.join(new_lines), encoding="utf-8")
    print("Inserted/updated Sources summary. Preview:")
    for l in summary_block:
        print(l, end='')


if __name__ == '__main__':
    raise SystemExit(main())
