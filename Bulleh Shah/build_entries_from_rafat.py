#!/usr/bin/env python3
"""
Ingest assembled Rafat OCR poems into Abshaar working entries.

LEGACY / DO NOT RUN AGAINST THE COMPLETED CORPUS: this helper predates the final
three-slot translation layout and can create entries that do not conform to the
current working template. It is retained as build provenance only. Update and
test its template before any future reuse.

Reads the per-poem files produced by assemble_rafat_poems.py (poem_XXX.txt, with
'-- URDU ... --' and '-- ENGLISH ... --' blocks). Correct the Urdu in those files
first, then run this to write data/working/bulleh_shah_XXXX.md entries in the
project format.

- Rafat poem N  ->  bulleh_shah_{N+offset:04d}  (default offset 1: poem 1 = 0002,
  which already exists as the manual "A for Allah", so it is skipped).
- Existing entry files are skipped unless --overwrite.
- Transliteration + literal gloss + tashreeh + key terms + themes are left as TODO.
- English (Rafat) is COPYRIGHTED -> recorded as literary translation, publish gate off.

Usage:
  python build_entries_from_rafat.py --poems rafat_poems --root "/path/to/Poetry Model Project"
"""
import os
import re
import glob
import argparse

URDU_HDR = "-- URDU"
ENG_HDR = "-- ENGLISH"

TEMPLATE = '''---
id: {id}
poet_id: bulleh_shah
title: "{title}"
work_type: "kafi"
source_ids:
  - source_rafat_selection
rights_status: "verify_before_publication"
review_status: "draft"
---

# Original

{urdu}

# Script Notes

- Script: Shahmukhi (Perso-Arabic)
- Language spans: Punjabi
- Notes: OCR draft (UTRNet) from Taufiq Rafat "A Selection" (Rafat poem {n}), corrected by reviewer. Verify against the page image; watch for dropped standalone alif and the swaps te/noon, dal/waw, fe/ghain.

# Transliteration

[TO DO: project-latin-v1 transliteration.]

# Literal Gloss

[TO DO (rauf): literal line-by-line English meaning.]

# Literary Translation

{english}

_Source: Taufiq Rafat, "Bulleh Shah: A Selection" (Vanguard, 1982), Rafat poem {n}. COPYRIGHTED - private reference only; do NOT publish._

# Tashreeh

[TO DO (rauf): metaphor, Sufi/cultural context, alternate readings.]

# Key Terms

- [TO DO (rauf): recurring terms + do_not_flatten_to notes]

# Themes

- [TO DO (rauf): themes]

# Source Notes

- Source ID: source_rafat_selection
- Source title: Bulleh Shah: A Selection, Rendered into English Verse (Taufiq Rafat, 1982)
- URL or bibliographic reference: Vanguard Books, Lahore, 1982 - Rafat poem {n}
- Rights status: Original Punjabi verse public domain; Rafat's English translation copyrighted (private reference only)
- Can this be published? no
- Can this be used for model training? no

# Review Notes

- Questions: Verify the OCR'd original against the page image.
- Uncertainties: OCR draft - check dropped alif and character swaps.
- Reviewer: (pending - rauf)
- Date: OCR draft + pairing; original corrected by reviewer; transliteration/interpretation pending
'''


def parse_poem_file(path):
    ubuf, ebuf, mode = [], [], None
    for ln in open(path, encoding="utf-8").read().splitlines():
        s = ln.strip()
        if s.startswith(URDU_HDR):
            mode = "u"; continue
        if s.startswith(ENG_HDR):
            mode = "e"; continue
        if s.startswith("====") or s.startswith("[urdu"):
            continue
        if mode == "u":
            ubuf.append(ln)
        elif mode == "e":
            ebuf.append(ln)
    return "\n".join(ubuf).strip(), "\n".join(ebuf).strip()


def first_line_title(urdu):
    for ln in urdu.splitlines():
        if ln.strip():
            return ln.strip()[:60]
    return "untitled"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poems", required=True, help="folder of poem_XXX.txt (from assemble_rafat_poems.py)")
    ap.add_argument("--root", required=True, help="Poetry Model Project root")
    ap.add_argument("--id-offset", type=int, default=1, help="Rafat poem N -> bulleh_shah_{N+offset}")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()

    working = os.path.join(a.root, "data", "working")
    os.makedirs(working, exist_ok=True)
    made = skipped = 0
    for f in sorted(glob.glob(os.path.join(a.poems, "poem_*.txt"))):
        m = re.search(r"poem_(\d+)\.txt$", os.path.basename(f))
        if not m:
            continue
        n = int(m.group(1))
        urdu, eng = parse_poem_file(f)
        if not urdu:
            skipped += 1; continue
        pid = "bulleh_shah_%04d" % (n + a.id_offset)
        out = os.path.join(working, pid + ".md")
        if os.path.exists(out) and not a.overwrite:
            skipped += 1; continue
        title = first_line_title(urdu).replace('"', "'")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(TEMPLATE.format(id=pid, title=title, urdu=urdu,
                                     english=(eng or "[TO DO: English not captured]"), n=n))
        made += 1
    print("Created %d entries, skipped %d -> %s" % (made, skipped, working))


if __name__ == "__main__":
    main()
