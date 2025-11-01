#!/usr/bin/env python3
"""
Remove English-like paragraphs that immediately follow a paragraph containing '**Metrics:**'.
This targets leftover abstract excerpts that followed removed '### Abstract (excerpt)' headings.

Creates a backup `<file>.bak2` before writing.
"""
from pathlib import Path
import shutil
import re


def is_english_paragraph(text: str) -> bool:
    # Heuristic: contains mainly ASCII letters/punctuation, at least 20 words, and contains sentence punctuation
    words = re.findall(r"\w+", text)
    if len(words) < 10:
        return False
    # ratio of ascii letters
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    if ascii_chars / max(1, len(text)) < 0.7:
        return False
    # has at least one period (.) indicating sentences
    if "." not in text:
        return False
    return True


def main():
    repo_root = Path(__file__).resolve().parents[1]
    target = repo_root / "data" / "medrxiv-ai-20251101-102613.md"
    if not target.exists():
        print(f"Target not found: {target}")
        return

    backup = target.with_suffix(target.suffix + ".bak2")
    shutil.copy2(target, backup)
    print(f"Backup written to: {backup}")

    text = target.read_text(encoding="utf-8")
    # split into paragraphs (preserve blank line boundaries)
    paragraphs = re.split(r"(\n\s*\n)", text)

    # paragraphs list alternates between content and separator due to split capturing
    out = []
    removed = 0
    i = 0
    while i < len(paragraphs):
        part = paragraphs[i]
        out.append(part)
        # if this part contains '**Metrics:**', check the next content paragraph
        if "**Metrics:**" in part:
            # next item is separator (if any) then next content; find next non-separator index
            j = i + 1
            # ensure we have a separator and a following paragraph
            if j + 1 < len(paragraphs):
                sep = paragraphs[j]
                next_para = paragraphs[j+1]
                # check heuristics on next_para
                if is_english_paragraph(next_para):
                    removed += 1
                    # skip the separator and next_para by advancing i
                    # but preserve a single separator for spacing
                    out.append(sep)
                    i = j + 2
                    continue
        i += 1

    if removed:
        target.write_text(''.join(out), encoding="utf-8")
    print(f"Removed {removed} english-like paragraphs after '**Metrics:**'")


if __name__ == "__main__":
    main()
