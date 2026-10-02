#!/usr/bin/env python3
"""Verify a written report.md against the data it was supposed to be written from.

The prose is written by a model, so the parts that must not be improvised get
checked by machine instead of trusted:

  * every paper's heat line matches the `heat_label` the fetcher computed
  * every arXiv link matches that paper's `abs_url`
  * no paper without measured heat is described with hype words
  * no paper without measured heat appears in the top-5 block
  * chapter and numbering structure is what build_site.py can parse

Exits non-zero on any problem, so run_weekly.sh can fail the run rather than
publish a report with an invented number in it.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Words that assert popularity. A paper with heat_source "none" has no evidence
# for any of them, so their presence in its write-up is a factual error.
HYPE = ["爆火", "爆红", "刷屏", "最热", "最火", "广受关注", "引发热议", "大量关注", "风靡", "炸裂"]

RE_CHAPTER = re.compile(r"^##\s+([一二三四五六七八九十]+)、\s*(.+?)\s*$")
RE_PAPER = re.compile(r"^###\s+(\d+)\.\s+(.*)$")
RE_ARXIV_LINK = re.compile(r"\[arXiv:([^\]]+)\]\(([^)]+)\)")
TOP_HEADING_MARK = "⭐"


def fail(problems, msg):
    problems.append(msg)


def load_papers(raw_dir, themes):
    """arxiv_id -> paper, across every theme file."""
    by_id = {}
    for slug in themes:
        path = raw_dir / f"{slug}.json"
        if not path.exists():
            continue
        for paper in json.loads(path.read_text(encoding="utf-8")).get("papers", []):
            by_id[paper["arxiv_id"]] = paper
    return by_id


def parse_report(md):
    """[(chapter_title, num, name, meta_line, body)], plus the top-5 block."""
    entries = []
    top_block = []
    chapter = None
    in_top = False
    current = None

    lines = md.splitlines()
    for i, raw in enumerate(lines):
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            in_top = TOP_HEADING_MARK in heading
            m = RE_CHAPTER.match(stripped)
            chapter = m.group(2) if m else (None if in_top else heading)
            current = None
            continue

        if in_top:
            if stripped:
                top_block.append(stripped)
            continue

        m = RE_PAPER.match(stripped)
        if m and chapter:
            # the metadata line is the first following line that carries the
            # arXiv link; the template puts the English title between them
            meta = ""
            for ahead in lines[i + 1 : i + 6]:
                if RE_ARXIV_LINK.search(ahead):
                    meta = ahead.strip()
                    break
            current = {
                "chapter": chapter,
                "num": int(m.group(1)),
                "name": m.group(2).strip(),
                "meta": meta,
                "body": [],
            }
            entries.append(current)
            continue

        if current is not None and stripped:
            current["body"].append(stripped)

    return entries, top_block


def fix_metadata_lines(md, papers):
    """Rebuild every paper's `<org> ｜ <heat> ｜ [arXiv:id](url)` line from data."""
    out = []
    fixed = 0
    for raw in md.splitlines():
        link = RE_ARXIV_LINK.search(raw)
        paper = papers.get(link.group(1)) if link else None
        # only metadata lines: they are the whole line, not prose containing a
        # citation, and the top-5 entries are numbered list items
        if paper and not raw.lstrip().startswith(("-", "*", "1.", "2.", "3.", "4.", "5.")):
            parts = []
            if paper.get("organization"):
                parts.append(paper["organization"])
            parts.append(paper.get("heat_label") or "热度未测得")
            parts.append(f"[arXiv:{paper['arxiv_id']}]({paper['abs_url']})")
            rebuilt = " ｜ ".join(parts)
            if rebuilt != raw.strip():
                fixed += 1
            out.append(rebuilt)
            continue
        out.append(raw)
    return "\n".join(out) + "\n", fixed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("date", help="YYYY-MM-DD of the report to check")
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument(
        "--fix",
        action="store_true",
        help="rewrite each paper's metadata line from the data before checking. "
        "Only that one line is touched, and it is fully derivable (organization, "
        "heat_label, abs_url), so this cannot invent anything - it just removes "
        "the need for the writer to transcribe it correctly.",
    )
    args = ap.parse_args()

    root = Path(args.root)
    report_path = root / "reports" / args.date / "report.md"
    raw_dir = root / "reports" / args.date / "raw"
    config = json.loads((root / "config" / "topics.json").read_text(encoding="utf-8"))
    themes = list(config["themes"])

    if not report_path.exists():
        sys.exit(f"no report at {report_path}")
    md = report_path.read_text(encoding="utf-8")
    papers = load_papers(raw_dir, themes)
    if not papers:
        sys.exit(f"no raw/*.json under {raw_dir} to check against")

    if args.fix:
        md, fixed = fix_metadata_lines(md, papers)
        if fixed:
            report_path.write_text(md, encoding="utf-8")
            print(f"[check] rewrote {fixed} metadata line(s) from the data",
                  file=sys.stderr)

    entries, top_block = parse_report(md)
    problems = []

    # ---- structure ----
    if not md.startswith("# "):
        fail(problems, "report does not start with a single H1 line")
    chapters = [c for c in dict.fromkeys(e["chapter"] for e in entries)]
    if len(chapters) != 6:
        fail(problems, f"expected 6 chapters, found {len(chapters)}: {chapters}")
    if not top_block:
        fail(problems, "no '## ⭐ ...' top-picks block found")

    seen_per_chapter = {}
    for entry in entries:
        seen_per_chapter.setdefault(entry["chapter"], []).append(entry["num"])
    for chapter, nums in seen_per_chapter.items():
        if nums != list(range(1, len(nums) + 1)):
            fail(problems, f"chapter 「{chapter}」 numbering is not 1..N: {nums}")

    # ---- per paper: the facts that must not be improvised ----
    checked = 0
    for entry in entries:
        link = RE_ARXIV_LINK.search(entry["meta"])
        if not link:
            fail(problems, f"「{entry['name']}」 has no arXiv link on its metadata line")
            continue
        arxiv_id, url = link.group(1), link.group(2)
        paper = papers.get(arxiv_id)
        if paper is None:
            fail(problems, f"「{entry['name']}」 cites {arxiv_id}, which is in no raw/*.json")
            continue
        checked += 1

        if url != paper["abs_url"]:
            fail(problems, f"{arxiv_id}: link is {url}, data says {paper['abs_url']}")

        expected = paper.get("heat_label")
        if expected and expected not in entry["meta"]:
            fail(problems, f"{arxiv_id}: heat line does not match data\n"
                           f"    report: {entry['meta']}\n"
                           f"    expect: ...{expected}...")

        # a star count in the prose is always wrong now: the fetcher stopped
        # emitting them precisely because they are often another repo's
        if re.search(r"\d[\d,.]*\s*(★|stars?\b)", entry["meta"]):
            fail(problems, f"{arxiv_id}: metadata line prints a star count; "
                           f"stars are not the paper's own often enough that the "
                           f"report must not quote them")

        if paper.get("heat_source") == "none":
            text = entry["meta"] + " " + " ".join(entry["body"])
            for word in HYPE:
                if word in text:
                    fail(problems, f"{arxiv_id}: has no measured heat but the "
                                   f"write-up says 「{word}」")

    # ---- top picks must have measured heat ----
    for line in top_block:
        for arxiv_id, _ in RE_ARXIV_LINK.findall(line):
            paper = papers.get(arxiv_id)
            if paper is None:
                fail(problems, f"top picks cite {arxiv_id}, which is in no raw/*.json")
            elif paper.get("heat_source") == "none":
                fail(problems, f"top picks include {arxiv_id}, which has no measured "
                               f"heat - that passes a zero-signal paper off as a hit")

    print(f"[check] {len(entries)} papers in 6 chapters, {checked} matched to data",
          file=sys.stderr)
    if problems:
        print(f"\n{len(problems)} problem(s):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)
    print("[check] report.md agrees with the fetched data", file=sys.stderr)


if __name__ == "__main__":
    main()
