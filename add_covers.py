#!/usr/bin/env -S uv run
# /// script
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""
Insert a Crisis issue cover thumbnail block into every article .qmd file.

For each article, derives the cover from citation.volume + citation.issue
(NOT the date: field, which is sometimes wrong) by globbing Images/ for the
matching YYYY-MM_vol_iss.jpg file, then injects an HTML block immediately
after the closing --- of the frontmatter.

Idempotent: skips files that already contain a .crisis-cover block.

Usage:
    python add_covers.py              # Process all articles
    python add_covers.py --dry-run    # Preview without writing
    python add_covers.py --volume 12  # One volume only
    python add_covers.py --limit 5    # Cap at N files
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
VOLUMES = ROOT / "Volumes"
IMAGES = ROOT / "Images"

MONTHS = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}

COVER_BLOCK = """```{{=html}}
<div class="crisis-cover">
  <a href="https://archive.org/download/sim_crisis_{stem}/sim_crisis_{stem}.pdf">
    <img src="/Images/{filename}" alt="Cover of The Crisis, {month} {year}">
  </a>
  <p><em>The Crisis</em><br>{month} {year}</p>
</div>
```"""


def split_frontmatter(text: str):
    """Return (frontmatter_dict, frontmatter_raw, body) or (None, '', text)."""
    if not text.startswith("---"):
        return None, "", text
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None, "", text
    raw = match.group(1)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return None, "", text
    body = text[match.end():]
    return data, match.group(0), body


def find_cover(volume, issue):
    """Glob Images/ for *_{vol}_{iss}.jpg. Returns Path or None."""
    matches = sorted(IMAGES.glob(f"*_{volume}_{issue}.jpg"))
    if len(matches) == 1:
        return matches[0]
    return None


def parse_cover_filename(name: str):
    """1934-05_41_5.jpg -> ('May', '1934'). Returns (None, None) on miss."""
    m = re.match(r"^(\d{4})-(\d{2})_\d+_\d+\.jpg$", name)
    if not m:
        return None, None
    year, month_num = m.group(1), m.group(2)
    return MONTHS.get(month_num), year


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--volume", type=str, help="Limit to a single volume")
    ap.add_argument("--limit", type=int, help="Max files to process")
    args = ap.parse_args()

    pattern = f"{args.volume}/**/*.qmd" if args.volume else "**/*.qmd"
    files = sorted(VOLUMES.glob(pattern))

    added = skipped_existing = skipped_no_citation = skipped_no_cover = errors = 0
    missing = []

    for path in files:
        if args.limit and added >= args.limit:
            break
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"ERR  {path.relative_to(ROOT)}: read failed ({e})", file=sys.stderr)
            errors += 1
            continue

        if "crisis-cover" in text:
            skipped_existing += 1
            continue

        data, fm_raw, body = split_frontmatter(text)
        if data is None:
            print(f"SKIP {path.relative_to(ROOT)}: no parseable frontmatter", file=sys.stderr)
            errors += 1
            continue

        citation = data.get("citation") or {}
        volume = citation.get("volume")
        issue = citation.get("issue")
        if volume is None or issue is None:
            skipped_no_citation += 1
            continue

        cover = find_cover(volume, issue)
        if not cover:
            skipped_no_cover += 1
            missing.append((str(path.relative_to(ROOT)), volume, issue))
            continue

        month, year = parse_cover_filename(cover.name)
        if not month:
            skipped_no_cover += 1
            missing.append((str(path.relative_to(ROOT)), volume, issue))
            continue

        stem = cover.stem  # e.g. 1934-05_41_5
        block = COVER_BLOCK.format(
            stem=stem, filename=cover.name, month=month, year=year
        )

        new_text = fm_raw + "\n" + block + "\n" + body.lstrip("\n")

        if args.dry_run:
            print(f"DRY  {path.relative_to(ROOT)}: would add {cover.name}")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"ADD  {path.relative_to(ROOT)}: {cover.name}")
        added += 1

    print()
    print(f"Added/would add:   {added}")
    print(f"Already had cover: {skipped_existing}")
    print(f"No citation block: {skipped_no_citation}")
    print(f"No matching cover: {skipped_no_cover}")
    print(f"Errors:            {errors}")
    if missing:
        print()
        print("Articles missing a cover (check Images/ or citation):")
        for path, vol, iss in missing[:20]:
            print(f"  {path}  (vol={vol}, issue={iss})")
        if len(missing) > 20:
            print(f"  ... and {len(missing) - 20} more")


if __name__ == "__main__":
    main()
