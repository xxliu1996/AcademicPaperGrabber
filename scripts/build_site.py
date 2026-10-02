#!/usr/bin/env python3
"""Turn reports/ into the static site under docs/, which GitHub Pages serves.

Reads every reports/<DATE>/report.md (plus raw/<theme>.json for the structured
bits) and emits:

    docs/index.html        the last three months
    docs/archive.html      everything, grouped by year
    docs/r/<DATE>.html     one rendered weekly report, chapters filterable
    docs/feed.xml          RSS
    docs/assets/site.css   shared styling
    docs/data/reports.json the same index as data, for anything else to read

Unlike the GitHub digest this project produces ONE report per week with six
chapters inside it, so the per-theme filtering happens within a page rather
than across pages.

Stdlib only, same as the grabber - the weekly run is unattended and must not
depend on a venv surviving between runs. Idempotent: it rebuilds docs/ from
scratch every time, so a deleted report disappears from the site instead of
lingering as an orphan page.
"""

import html
import json
import re
import shutil
import sys
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
DOCS = ROOT / "docs"
CONFIG = ROOT / "config" / "topics.json"

SITE_URL = "https://xxliu1996.github.io/AcademicPaperGrabber"
SITE_TITLE = "AI 论文周报"
SITE_TAGLINE = "每周日自动抓取六个方向最近一周的热门论文，每个方向 10 篇，人读的那种周报。"

# Reports older than this fall off the front page into the archive.
RECENT_DAYS = 92

# The exact heading the weekly template uses for the cross-theme picks.
TOP_HEADING = "⭐ 本周最值得读的 5 篇"


def info(msg):
    print(f"[site] {msg}", file=sys.stderr)


def warn(msg):
    print(f"WARN: {msg}", file=sys.stderr)


# --------------------------------------------------------------------------
# Markdown subset renderer
#
# Not a general Markdown implementation on purpose. report.md is written to the
# fixed template in .claude/commands/papers-weekly.md, so the handful of
# constructs below is all that ever appears. A real parser would be more code
# and more failure modes for no gain here.
# --------------------------------------------------------------------------

RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
RE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
RE_CODE = re.compile(r"`([^`]+)`")


def inline(text):
    """Escape first, then re-introduce the few inline constructs we allow. In
    this order a paper title containing < or & cannot inject markup."""
    out = html.escape(text, quote=False)
    out = RE_CODE.sub(r"<code>\1</code>", out)
    out = RE_LINK.sub(
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', out
    )
    out = RE_BOLD.sub(r"<strong>\1</strong>", out)
    return out


def render_block(lines):
    """Render a run of body lines (paragraphs, bullets, quotes, ordered lists)."""
    out = []
    para, bullets, quote, ordered = [], [], [], []

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()
        if bullets:
            out.append('<ul class="facets">' + "".join(f"<li>{inline(b)}</li>" for b in bullets) + "</ul>")
            bullets.clear()
        if ordered:
            out.append('<ol class="picks">' + "".join(f"<li>{inline(b)}</li>" for b in ordered) + "</ol>")
            ordered.clear()
        if quote:
            out.append(f'<blockquote>{inline(" ".join(quote))}</blockquote>')
            quote.clear()

    for raw in lines:
        stripped = raw.strip()
        if not stripped:
            flush()
            continue
        if set(stripped) <= {"-"} and len(stripped) >= 3:
            flush()
            continue  # horizontal rule: the card borders already separate things
        if stripped.startswith("> "):
            if para or bullets or ordered:
                flush()
            quote.append(stripped[2:].strip())
            continue
        if stripped.startswith(("- ", "* ")):
            if para or quote or ordered:
                flush()
            bullets.append(stripped[2:].strip())
            continue
        m = re.match(r"^\d+\.\s+(.*)", stripped)
        if m:
            if para or quote or bullets:
                flush()
            ordered.append(m.group(1))
            continue
        if bullets or quote or ordered:
            flush()
        para.append(stripped)

    flush()
    return "\n".join(out)


# --------------------------------------------------------------------------
# Parsing one weekly report
# --------------------------------------------------------------------------

RE_CHAPTER = re.compile(r"^##\s+(?:[一二三四五六七八九十]+、)?\s*(.+?)\s*$")
RE_PAPER = re.compile(r"^###\s+(\d+)\.\s+(.*)$")


def parse_report(md, theme_by_title):
    """Split report.md into title / lede / top picks / chapters.

    Chapter headings are matched back to theme slugs by their configured title,
    so `## 三、Agent` becomes the `agent` chapter. An unrecognised heading still
    renders - it just gets no slug and therefore no filter chip.
    """
    title = ""
    lede_lines, top_lines = [], []
    chapters = []
    current, paper = None, None
    mode = "lede"

    for raw in md.splitlines():
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("# "):
            title = stripped[2:].strip()
            continue

        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            if heading == TOP_HEADING or heading.startswith("⭐"):
                mode, paper = "top", None
                continue
            m = RE_CHAPTER.match(stripped)
            name = m.group(1) if m else heading
            current = {
                "title": name,
                "slug": theme_by_title.get(name),
                "papers": [],
                "preamble": [],
            }
            chapters.append(current)
            mode, paper = "chapter", None
            continue

        if stripped.startswith("### ") and mode == "chapter" and current is not None:
            m = RE_PAPER.match(stripped)
            paper = {
                "num": m.group(1) if m else "",
                "name": (m.group(2) if m else stripped[4:]).strip(),
                "lines": [],
            }
            current["papers"].append(paper)
            continue

        if mode == "lede":
            lede_lines.append(line)
        elif mode == "top":
            top_lines.append(line)
        elif paper is not None:
            paper["lines"].append(line)
        elif current is not None:
            current["preamble"].append(line)

    if not chapters:
        warn("report has no '## ' chapters - the site page will be nearly empty")

    return {
        "title": title,
        "lede_html": render_block(lede_lines),
        "top_html": render_block(top_lines),
        "chapters": chapters,
    }


def load_config():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    themes = {k: v for k, v in cfg["themes"].items()}
    by_title = {spec.get("title", slug): slug for slug, spec in themes.items()}
    return themes, by_title


def collect(themes, by_title):
    """Every weekly report on disk, newest first."""
    found = []
    if not REPORTS.exists():
        return found
    for date_dir in sorted(REPORTS.iterdir(), reverse=True):
        if not date_dir.is_dir() or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_dir.name):
            continue
        md_path = date_dir / "report.md"
        if not md_path.exists():
            continue
        try:
            md = md_path.read_text(encoding="utf-8")
        except OSError as exc:
            warn(f"cannot read {md_path}: {exc}")
            continue

        parsed = parse_report(md, by_title)

        # raw/ carries week bounds and how many of the candidates had a
        # measured heat signal - worth surfacing, since it is the honest
        # caveat on the whole ranking.
        week_start, week_end, measured = "", date_dir.name, 0
        for slug in themes:
            raw_path = date_dir / "raw" / f"{slug}.json"
            if not raw_path.exists():
                continue
            try:
                raw = json.loads(raw_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                warn(f"cannot parse {raw_path}: {exc}")
                continue
            week_start = raw.get("week_start") or week_start
            week_end = raw.get("week_end") or week_end
            measured += raw.get("measured_heat_count") or 0

        counts = {c["slug"] or c["title"]: len(c["papers"]) for c in parsed["chapters"]}
        total = sum(counts.values())
        if total == 0:
            warn(f"{md_path} parsed 0 papers - check the '### N. 名称' headings")

        found.append(
            {
                "date": date_dir.name,
                "title": parsed["title"] or f"AI 论文周报 {date_dir.name}",
                "week_start": week_start,
                "week_end": week_end,
                "measured_heat_count": measured,
                "counts": counts,
                "count": total,
                "parsed": parsed,
                "slug": date_dir.name,
            }
        )
    return found


# --------------------------------------------------------------------------
# Page templates
# --------------------------------------------------------------------------

def shell(title, body, css_depth=0, extra_head=""):
    prefix = "../" * css_depth
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{prefix}assets/site.css">
<link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_TITLE)}" href="{prefix}feed.xml">
{extra_head}
</head>
<body>
{body}
</body>
</html>
"""


def chapter_chips(themes, chapters):
    """Filter chips for the chapters actually present in this report."""
    chips = ['<button class="chip is-on" data-theme="all">全部</button>']
    for chap in chapters:
        slug = chap["slug"]
        if not slug:
            continue
        accent = themes.get(slug, {}).get("accent", "#2f6f5e")
        chips.append(
            f'<button class="chip" data-theme="{slug}" style="--chip:{accent}">'
            f'{html.escape(chap["title"])}<span class="chip-n">{len(chap["papers"])}</span></button>'
        )
    return f'<div class="chips">{"".join(chips)}</div>'


def card(rep, themes, depth=0):
    prefix = "../" * depth
    bars = []
    for slug, n in rep["counts"].items():
        accent = themes.get(slug, {}).get("accent", "#2f6f5e")
        title = themes.get(slug, {}).get("title", slug)
        bars.append(
            f'<li><span class="dot" style="background:{accent}"></span>'
            f'{html.escape(title)}<b>{n}</b></li>'
        )
    return f"""
<article class="card">
  <div class="card-head">
    <span class="badge">周报</span>
    <time>{rep['date']}</time>
  </div>
  <h3><a href="{prefix}r/{rep['slug']}.html">{html.escape(rep['title'])}</a></h3>
  <ul class="card-counts">{''.join(bars)}</ul>
  <div class="card-foot">
    <span>{rep['count']} 篇</span>
    <a class="go" href="{prefix}r/{rep['slug']}.html">阅读 →</a>
  </div>
</article>
"""


FILTER_JS = """
<script>
  // Chapter filtering is client-side so the whole site stays static files.
  document.addEventListener('click', function (e) {
    var chip = e.target.closest('.chip');
    if (!chip) return;
    var want = chip.dataset.theme;
    document.querySelectorAll('.chip').forEach(function (c) { c.classList.toggle('is-on', c === chip); });
    document.querySelectorAll('.chapter').forEach(function (ch) {
      ch.hidden = want !== 'all' && ch.dataset.theme !== want;
    });
  });
</script>
"""


def build_report_page(rep, reports, themes):
    parsed = rep["parsed"]
    blocks = []

    if parsed["lede_html"]:
        blocks.append(f'<div class="lede">{parsed["lede_html"]}</div>')
    if parsed["top_html"]:
        blocks.append(
            f'<section class="top"><h2>{html.escape(TOP_HEADING)}</h2>{parsed["top_html"]}</section>'
        )

    blocks.append(chapter_chips(themes, parsed["chapters"]))

    for chap in parsed["chapters"]:
        slug = chap["slug"] or ""
        spec = themes.get(slug, {})
        accent = spec.get("accent", "#2f6f5e")
        papers = []
        for p in chap["papers"]:
            papers.append(
                f'<section class="paper">'
                f'<h3><span class="num">{html.escape(p["num"])}</span>{inline(p["name"])}</h3>'
                f'{render_block(p["lines"])}</section>'
            )
        preamble = render_block(chap["preamble"])
        subtitle = spec.get("subtitle") or ""
        sub_html = f'<p class="chapter-sub">{html.escape(subtitle)}</p>' if subtitle else ""
        anchor = html.escape(slug or chap["title"], quote=True)
        blocks.append(
            f'<div class="chapter" data-theme="{html.escape(slug, quote=True)}" '
            f'style="--accent:{accent}" id="{anchor}">'
            f'<h2>{html.escape(chap["title"])}'
            f'<span class="chapter-n">{len(chap["papers"])} 篇</span></h2>'
            f'{sub_html}{preamble}{"".join(papers)}</div>'
        )

    idx = reports.index(rep)
    nav = []
    if idx > 0:
        nav.append(f'<a href="{reports[idx - 1]["slug"]}.html">← 更新一期（{reports[idx - 1]["date"]}）</a>')
    if idx + 1 < len(reports):
        nav.append(f'<a href="{reports[idx + 1]["slug"]}.html">更早一期（{reports[idx + 1]["date"]}）→</a>')

    window = f'{rep["week_start"]} – {rep["week_end"]}' if rep["week_start"] else rep["date"]

    body = f"""
<div class="page report">
  <header class="cover">
    <a class="back" href="../index.html">← 返回首页</a>
    <h1>{html.escape(rep['title'])}</h1>
    <div class="meta">
      <span>{window}</span>
      <span>{rep['count']} 篇</span>
    </div>
  </header>

  {''.join(blocks)}

  <nav class="pager">{''.join(nav)}</nav>
  <footer class="foot">
    <a href="../index.html">← 返回首页</a>
    <a href="../archive.html">历史归档</a>
    <a href="../feed.xml">RSS</a>
  </footer>
</div>
{FILTER_JS}
"""
    return shell(f"{rep['title']} · {SITE_TITLE}", body, css_depth=1)


def build_index(reports, themes):
    cutoff = date.today() - timedelta(days=RECENT_DAYS)
    recent = [r for r in reports if _as_date(r["date"]) >= cutoff]
    older = len(reports) - len(recent)
    cards = "".join(card(r, themes) for r in recent)
    empty = '<p class="empty">最近三个月还没有报告。</p>' if not recent else ""

    legend = "".join(
        f'<li><span class="dot" style="background:{spec.get("accent", "#2f6f5e")}"></span>'
        f'{html.escape(spec.get("title", slug))}'
        f'<em>{html.escape(spec.get("subtitle", ""))}</em></li>'
        for slug, spec in themes.items()
    )

    body = f"""
<div class="page">
  <header class="cover">
    <h1>{html.escape(SITE_TITLE)}</h1>
    <p class="subtitle">{html.escape(SITE_TAGLINE)}</p>
  </header>

  <ul class="legend">{legend}</ul>

  <p class="scope">最近三个月 {len(recent)} 期。
  {f'更早的 {older} 期在<a href="archive.html">历史归档</a>。' if older else ''}</p>

  {empty}
  <div class="grid">{cards}</div>

  <footer class="foot">
    <a href="archive.html">历史归档 →</a>
    <a href="feed.xml">RSS</a>
    <span>数据源：Hugging Face Papers + arXiv API</span>
  </footer>
</div>
"""
    return shell(SITE_TITLE, body)


def build_archive(reports, themes):
    by_year = {}
    for r in reports:
        by_year.setdefault(r["date"][:4], []).append(r)
    groups = []
    for year in sorted(by_year, reverse=True):
        cards = "".join(card(r, themes) for r in by_year[year])
        groups.append(
            f'<div class="year"><h2>{year} 年 · {len(by_year[year])} 期</h2>'
            f'<div class="grid">{cards}</div></div>'
        )

    body = f"""
<div class="page">
  <header class="cover">
    <a class="back" href="index.html">← 返回首页</a>
    <h1>历史归档</h1>
    <p class="subtitle">全部 {len(reports)} 期周报，按年份倒序。</p>
  </header>

  {''.join(groups)}

  <footer class="foot">
    <a href="index.html">← 返回首页</a>
    <a href="feed.xml">RSS</a>
  </footer>
</div>
"""
    return shell(f"历史归档 · {SITE_TITLE}", body)


def build_feed(reports):
    items = []
    for rep in reports[:20]:
        link = f"{SITE_URL}/r/{rep['slug']}.html"
        summary = re.sub(r"<[^>]+>", " ", rep["parsed"]["lede_html"])
        summary = re.sub(r"\s+", " ", summary).strip()[:600]
        counts = "；".join(f"{k} {v} 篇" for k, v in rep["counts"].items())
        try:
            pub = format_datetime(
                datetime.strptime(rep["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            )
        except ValueError:
            pub = format_datetime(datetime.now(timezone.utc))
        items.append(
            f"""  <item>
    <title>{html.escape(rep['title'])}</title>
    <link>{link}</link>
    <guid isPermaLink="true">{link}</guid>
    <pubDate>{pub}</pubDate>
    <description>{html.escape(summary + (' ｜ ' + counts if counts else ''))}</description>
  </item>"""
        )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{html.escape(SITE_TITLE)}</title>
  <link>{SITE_URL}/</link>
  <description>{html.escape(SITE_TAGLINE)}</description>
  <language>zh-CN</language>
  <lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""


def _as_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


# --------------------------------------------------------------------------

CSS = """
/* Shared styling: warm paper background, serif CJK, one accent per chapter. */
:root {
  --bg: #faf9f7;
  --bg-card: #ffffff;
  --text: #1f2320;
  --text-dim: #5b6560;
  --border: #e4e1da;
  --accent: #2f6f5e;
  --accent-soft: #e8f2ee;
  font-family: "Songti SC", "Noto Serif SC", "PingFang SC", "Hiragino Sans GB", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #161915; --bg-card: #1f231e; --text: #e8e6e0;
    --text-dim: #a3a89e; --border: #333a32; --accent-soft: #23342c;
  }
}
:root[data-theme="dark"] {
  --bg: #161915; --bg-card: #1f231e; --text: #e8e6e0;
  --text-dim: #a3a89e; --border: #333a32; --accent-soft: #23342c;
}

* { box-sizing: border-box; }
body { background: var(--bg); color: var(--text); margin: 0; line-height: 1.75; }
a { color: var(--accent); }
.page { max-width: 900px; margin: 0 auto; padding: 48px 24px 96px; }

.cover h1 { font-size: 2.1rem; margin: 0 0 8px; letter-spacing: 0.02em; }
.cover .subtitle { color: var(--text-dim); font-size: 1rem; margin: 0 0 20px; }
.back { display: inline-block; font-size: 0.85rem; color: var(--text-dim); text-decoration: none; margin-bottom: 16px; }
.back:hover { color: var(--accent); }
.scope { color: var(--text-dim); font-size: 0.9rem; margin: 24px 0 12px; }
.empty { color: var(--text-dim); padding: 32px 0; }

/* ---- theme legend on the front page ---- */
.legend { list-style: none; padding: 0; margin: 24px 0 8px; display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 6px 18px; }
.legend li { font-size: 0.9rem; display: flex; align-items: baseline; gap: 7px; }
.legend em { color: var(--text-dim); font-style: normal; font-size: 0.8rem; }
.dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }

/* ---- chapter filter ---- */
.chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 28px 0 8px; position: sticky;
  top: 0; background: var(--bg); padding: 10px 0; z-index: 5; }
.chip {
  --chip: var(--accent);
  font: inherit; font-size: 0.85rem; cursor: pointer;
  padding: 5px 14px; border-radius: 999px;
  border: 1px solid var(--border); background: var(--bg-card); color: var(--text-dim);
}
.chip:hover { border-color: var(--chip); color: var(--chip); }
.chip.is-on { background: var(--chip); border-color: var(--chip); color: #fff; font-weight: 600; }
.chip-n { margin-left: 6px; opacity: 0.7; font-size: 0.78em; }

/* ---- listings ---- */
.year { margin: 32px 0; }
.year h2 { font-size: 1.05rem; color: var(--text-dim); font-weight: 600;
  border-bottom: 1px solid var(--border); padding-bottom: 6px; margin-bottom: 16px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; }

.card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-top: 3px solid var(--accent); border-radius: 10px;
  padding: 16px 18px; display: flex; flex-direction: column;
}
.card-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 999px;
  font-size: 0.75rem; font-weight: 600; background: var(--accent); color: #fff; }
.card-head time { color: var(--text-dim); font-size: 0.8rem; }
.card h3 { font-size: 1.05rem; margin: 10px 0 8px; line-height: 1.5; }
.card h3 a { text-decoration: none; color: var(--text); }
.card h3 a:hover { color: var(--accent); }
.card-counts { list-style: none; padding: 0; margin: 0 0 12px; font-size: 0.82rem;
  color: var(--text-dim); display: grid; grid-template-columns: 1fr 1fr; gap: 1px 10px; }
.card-counts li { display: flex; align-items: center; gap: 6px; }
.card-counts b { margin-left: auto; color: var(--text); font-weight: 600; }
.card-foot { margin-top: auto; display: flex; justify-content: space-between;
  align-items: center; font-size: 0.8rem; color: var(--text-dim); }
.card-foot .go { text-decoration: none; font-weight: 600; }

/* ---- a single weekly report ---- */
.report .meta { display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
  font-size: 0.85rem; color: var(--text-dim); margin-bottom: 8px; }
.report .lede { font-size: 1.02rem; margin: 24px 0 8px; padding: 16px 20px;
  background: var(--accent-soft); border-radius: 10px; }
.report .lede p:first-child { margin-top: 0; }
.report .lede p:last-child { margin-bottom: 0; }

section.top { margin: 20px 0 8px; padding: 4px 22px 16px; border: 1px solid var(--border);
  border-left: 4px solid #c08a2e; border-radius: 10px; background: var(--bg-card); }
section.top h2 { font-size: 1.1rem; margin: 16px 0 4px; }
ol.picks { padding-left: 1.4em; margin: 8px 0; }
ol.picks li { margin: 6px 0; font-size: 0.95rem; }

.chapter { margin: 36px 0; }
.chapter[hidden] { display: none; }
.chapter > h2 { font-size: 1.3rem; margin: 0 0 4px; padding-bottom: 6px;
  border-bottom: 2px solid var(--accent); display: flex; align-items: baseline; gap: 10px; }
.chapter-n { font-size: 0.78rem; font-weight: 400; color: var(--text-dim); margin-left: auto; }
.chapter-sub { color: var(--text-dim); font-size: 0.85rem; margin: 0 0 12px; }

section.paper {
  background: var(--bg-card); border: 1px solid var(--border);
  border-left: 4px solid var(--accent); border-radius: 10px;
  padding: 4px 22px 16px; margin: 14px 0;
}
section.paper h3 { font-size: 1.08rem; margin: 16px 0 6px; line-height: 1.5; }
section.paper h3 .num { color: var(--accent); font-weight: 700; margin-right: 8px; }
/* The line right under a paper heading is the English title + heat + link. */
section.paper > p:first-of-type { margin: 4px 0 10px; font-size: 0.88rem; color: var(--text-dim); }
ul.facets { margin: 8px 0; padding-left: 1.2em; }
ul.facets li { margin: 5px 0; font-size: 0.93rem; }
blockquote { margin: 10px 0; padding: 8px 14px; color: var(--text-dim);
  border-left: 2px solid var(--border); font-size: 0.92rem; }
code { background: var(--accent-soft); padding: 1px 5px; border-radius: 4px; font-size: 0.88em; }

.pager { display: flex; justify-content: space-between; gap: 12px; margin: 48px 0 0; font-size: 0.9rem; }
.pager a { text-decoration: none; }
.foot { margin-top: 56px; padding-top: 16px; border-top: 1px solid var(--border);
  color: var(--text-dim); font-size: 0.85rem;
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 12px; }

@media (max-width: 600px) {
  .page { padding: 32px 16px 64px; }
  .cover h1 { font-size: 1.6rem; }
  .grid { grid-template-columns: 1fr; }
  .card-counts { grid-template-columns: 1fr; }
  .pager { flex-direction: column; }
}
"""


def main():
    themes, by_title = load_config()
    reports = collect(themes, by_title)
    if not reports:
        sys.exit("no reports found under reports/ - nothing to build")

    # Rebuild from scratch so deleted reports do not linger as orphan pages.
    if DOCS.exists():
        shutil.rmtree(DOCS)
    (DOCS / "r").mkdir(parents=True)
    (DOCS / "assets").mkdir()
    (DOCS / "data").mkdir()

    # Pages is Jekyll-backed by default and would skip anything it considers
    # special; this opts the whole site out of that processing.
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "assets" / "site.css").write_text(CSS.strip() + "\n", encoding="utf-8")

    for rep in reports:
        (DOCS / "r" / f"{rep['slug']}.html").write_text(
            build_report_page(rep, reports, themes), encoding="utf-8"
        )

    (DOCS / "index.html").write_text(build_index(reports, themes), encoding="utf-8")
    (DOCS / "archive.html").write_text(build_archive(reports, themes), encoding="utf-8")
    (DOCS / "feed.xml").write_text(build_feed(reports), encoding="utf-8")

    index_data = [
        {
            "date": r["date"],
            "title": r["title"],
            "week_start": r["week_start"],
            "week_end": r["week_end"],
            "count": r["count"],
            "counts": r["counts"],
            "measured_heat_count": r["measured_heat_count"],
            "slug": r["slug"],
            "url": f"{SITE_URL}/r/{r['slug']}.html",
        }
        for r in reports
    ]
    (DOCS / "data" / "reports.json").write_text(
        json.dumps(index_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    info(f"built {len(reports)} weekly reports -> docs/")
    for r in reports[:3]:
        info(f"  {r['date']}: {r['count']} 篇 "
             f"({', '.join(f'{k}:{v}' for k, v in r['counts'].items())})")


if __name__ == "__main__":
    main()
