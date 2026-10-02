#!/usr/bin/env python3
"""Collect the past week's hottest papers across six AI themes.

Deterministic and stdlib-only. Two sources, and only one of them carries a real
popularity signal:

  1. Hugging Face daily papers (https://huggingface.co/api/daily_papers) - the
     only public endpoint anywhere that exposes a per-paper popularity number
     (`upvotes`), plus a linked GitHub repo and its star count. Covers roughly
     50 papers a week, overwhelmingly LLM / VLM / agent.
  2. The arXiv API - unlimited coverage (cs.RO alone runs ~680 papers a week)
     but NO popularity signal of any kind.

So for most arXiv papers the ranking is "topic fit + has code + recent", not
measured heat. Every emitted paper therefore carries a `heat_source` field
("hf" / "github" / "none") and the agent writing the report is required to
label it honestly rather than implying heat that was never measured.

The agent that calls this writes the prose; this script never editorializes.
"""

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "topics.json"

UA = "AcademicPaperGrabber/1.0 (+https://github.com/topics/academicpapergrabber)"
HF_API = "https://huggingface.co/api/daily_papers"
ARXIV_API = "https://export.arxiv.org/api/query"
GITHUB_API = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"


def warn(msg):
    print(f"WARN: {msg}", file=sys.stderr)


def info(msg):
    print(f"[grab] {msg}", file=sys.stderr)


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def fetch_text(url, headers=None, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_json(url, headers=None, retries=3, timeout=40):
    """GET and parse JSON, retrying on transient failures. None on give-up."""
    for attempt in range(retries):
        try:
            return json.loads(fetch_text(url, headers=headers, timeout=timeout))
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 429, 500, 502, 503):
                if attempt == retries - 1:
                    warn(f"HTTP {exc.code} on {url}, giving up")
                    return None
                wait = _retry_after(exc)
                info(f"HTTP {exc.code} on {url}, sleeping {wait}s")
                time.sleep(wait)
                continue
            if exc.code == 404:
                return None
            warn(f"HTTP {exc.code} on {url}")
            return None
        except Exception as exc:  # noqa: BLE001 - one bad call must not kill the run
            if attempt == retries - 1:
                warn(f"{type(exc).__name__} on {url}: {exc}")
                return None
            time.sleep(3)
    return None


def _retry_after(exc):
    """Seconds to sleep, from Retry-After or x-ratelimit-reset. Capped so a
    weekly run never hangs for the full hour of an exhausted GitHub quota."""
    retry_after = exc.headers.get("Retry-After")
    if retry_after and retry_after.isdigit():
        return min(int(retry_after), 90)
    reset = exc.headers.get("x-ratelimit-reset")
    if reset and reset.isdigit():
        delta = int(reset) - int(time.time()) + 2
        if delta > 0:
            return min(delta, 90)
    return 20


# --------------------------------------------------------------------------
# Source 1: Hugging Face daily papers (the only measured heat signal)
# --------------------------------------------------------------------------

def normalize_arxiv_id(raw):
    """'http://arxiv.org/abs/2609.40361v1' / '2609.40361v1' -> '2609.40361'."""
    if not raw:
        return None
    tail = raw.rstrip("/").split("/")[-1]
    return re.sub(r"v\d+$", "", tail).strip()


def fetch_hf_window(start_date, end_date, max_pages=6):
    """Every HF daily paper whose arXiv date OR daily-feature date falls in the
    window, keyed by bare arXiv id.

    Queried day by day rather than with one big `limit=` call: the flat listing
    is newest-first and `limit` is capped at 100 by the server, so a busy week
    would silently truncate the far end of the window. One query per day, paged
    with `p=`, is bounded and exact - a single day really does run past 100
    papers (2026-09-29 had 109). The extra `sort=trending` call catches papers
    HF itself still considers hot though they were featured before the window.
    """
    papers = {}
    requests = []
    day = start_date
    while day <= end_date:
        requests.append(("date", day.isoformat()))
        day += timedelta(days=1)
    requests.append(("sort", "trending"))

    for kind, value in requests:
        for page in range(max_pages):
            url = f"{HF_API}?{kind}={value}&limit=100&p={page}"
            data = fetch_json(url)
            if not isinstance(data, list):
                if page == 0:
                    warn(f"HF returned no list for {url}")
                break
            kept = _absorb_hf_page(data, papers, start_date, end_date)
            if kept:
                info(f"HF {kind}={value} p{page}: {kept} in-window")
            if len(data) < 100:
                break
            if kind == "sort":
                break  # the trending list is a top-up, one page is enough

    info(f"HF total: {len(papers)} papers in window, max upvotes="
         f"{max((p['hf_upvotes'] for p in papers.values()), default=0)}")
    return papers


def _absorb_hf_page(data, papers, start_date, end_date):
    kept = 0
    for item in data:
        paper = item.get("paper") or {}
        arxiv_id = normalize_arxiv_id(paper.get("id"))
        if not arxiv_id:
            continue
        published = (paper.get("publishedAt") or item.get("publishedAt") or "")[:10]
        featured = (paper.get("submittedOnDailyAt") or "")[:10]
        if not _in_window(published, start_date, end_date) and not _in_window(
            featured, start_date, end_date
        ):
            continue
        upvotes = paper.get("upvotes") or 0
        prev = papers.get(arxiv_id)
        if prev and (prev.get("hf_upvotes") or 0) >= upvotes:
            continue
        org = paper.get("organization") or item.get("organization") or {}
        papers[arxiv_id] = {
            "arxiv_id": arxiv_id,
            "title": _squash(paper.get("title") or item.get("title") or ""),
            "abstract": _squash(paper.get("summary") or item.get("summary") or ""),
            "authors": [a.get("name") for a in paper.get("authors") or [] if a.get("name")],
            "hf_upvotes": upvotes,
            "hf_url": f"https://huggingface.co/papers/{arxiv_id}",
            "github_repo": paper.get("githubRepo") or None,
            # A submitter attached this link on HF, so it really is the paper's
            # own repo - unlike a link mined out of an abstract.
            "github_repo_source": "hf" if paper.get("githubRepo") else None,
            "github_stars": paper.get("githubStars"),
            "project_page": paper.get("projectPage") or None,
            "organization": org.get("fullname") or org.get("name") or None,
            "hf_published": published or None,
            "hf_featured": featured or None,
        }
        kept += 1
    return kept


def _in_window(date_str, start_date, end_date):
    if not date_str or len(date_str) < 10:
        return False
    try:
        d = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except ValueError:
        return False
    return start_date <= d <= end_date


def _squash(text):
    """arXiv and HF both hard-wrap abstracts; collapse to one line."""
    return re.sub(r"\s+", " ", (text or "")).strip()


# --------------------------------------------------------------------------
# Source 2: the arXiv API (coverage, no heat signal)
# --------------------------------------------------------------------------

def arxiv_get(params, retries=5):
    """One arXiv API call. Returns the parsed Atom root, or None.

    arXiv answers 429 when it thinks you are hammering it - two full runs back
    to back is enough - and it does not recover in a few seconds. A 5s retry
    just burns the remaining attempts and the theme ends up with an empty
    candidate pool that looks like a quiet week. So back off in tens of
    seconds, honouring Retry-After when it is sent.
    """
    url = f"{ARXIV_API}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            return ET.fromstring(fetch_text(url, timeout=60))
        except urllib.error.HTTPError as exc:
            last = attempt == retries - 1
            if exc.code in (429, 503) and not last:
                # Escalating, not linear: once arXiv starts throttling it stays
                # unhappy for minutes, and three full runs in one afternoon is
                # all it takes. 30 / 60 / 120 / 240s.
                wait = max(_retry_after(exc), 30 * (2 ** attempt))
                info(f"arXiv {exc.code}, backing off {wait}s "
                     f"(attempt {attempt + 1}/{retries})")
                time.sleep(wait)
                continue
            warn(f"arXiv HTTP {exc.code} for {params.get('search_query', params)}")
            return None
        except Exception as exc:  # noqa: BLE001
            if attempt == retries - 1:
                warn(f"arXiv call failed ({type(exc).__name__}: {exc}) for {params}")
                return None
            time.sleep(10)
    return None


def parse_arxiv_entries(root):
    out = []
    for entry in root.findall(f"{ATOM}entry"):
        arxiv_id = normalize_arxiv_id((entry.findtext(f"{ATOM}id") or ""))
        if not arxiv_id:
            continue
        cats = [c.get("term") for c in entry.findall(f"{ATOM}category") if c.get("term")]
        primary = entry.find(f"{ARXIV_NS}primary_category")
        pdf_url = None
        for link in entry.findall(f"{ATOM}link"):
            if link.get("title") == "pdf":
                pdf_url = link.get("href")
        out.append(
            {
                "arxiv_id": arxiv_id,
                "title": _squash(entry.findtext(f"{ATOM}title")),
                "abstract": _squash(entry.findtext(f"{ATOM}summary")),
                "authors": [
                    _squash(a.findtext(f"{ATOM}name"))
                    for a in entry.findall(f"{ATOM}author")
                    if a.findtext(f"{ATOM}name")
                ],
                "published": (entry.findtext(f"{ATOM}published") or "")[:10],
                "updated": (entry.findtext(f"{ATOM}updated") or "")[:10],
                "primary_category": primary.get("term") if primary is not None else (cats[0] if cats else None),
                "categories": cats,
                "comment": _squash(entry.findtext(f"{ARXIV_NS}comment") or "") or None,
                "abs_url": f"https://arxiv.org/abs/{arxiv_id}",
                "pdf_url": pdf_url or f"https://arxiv.org/pdf/{arxiv_id}",
            }
        )
    return out


def build_query(cats, terms, start_date, end_date):
    """`(cat:A OR cat:B) AND (abs:"t1" OR abs:"t2") AND submittedDate:[...]`.

    Dates are inclusive on both ends; arXiv wants UTC `YYYYMMDDHHMM`.
    """
    cat_clause = " OR ".join(f"cat:{c}" for c in cats)
    term_clause = " OR ".join(f'abs:"{t}"' for t in terms)
    lo = start_date.strftime("%Y%m%d") + "0000"
    hi = end_date.strftime("%Y%m%d") + "2359"
    return f"({cat_clause}) AND ({term_clause}) AND submittedDate:[{lo} TO {hi}]"


def fetch_arxiv_query(query, max_results, sleep_seconds, page_size=100):
    """Paginate one arXiv search, newest first.

    Returns (entries, complete). `complete` is False when a page could not be
    fetched at all, so the caller can mark the theme's output as built on
    partial data instead of passing it off as the week's full picture.
    """
    collected = []
    complete = True
    start = 0
    while len(collected) < max_results:
        root = arxiv_get(
            {
                "search_query": query,
                "start": start,
                "max_results": min(page_size, max_results - len(collected)),
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
        )
        if root is None:
            complete = False
            break
        total = root.findtext(f"{OPENSEARCH}totalResults")
        batch = parse_arxiv_entries(root)
        if start == 0:
            info(f"  arXiv total={total or '?'} for {query[:70]}...")
            if not batch and total not in (None, "0"):
                warn("arXiv returned 0 parsed entries for a non-empty result set "
                     "- the Atom schema may have changed")
        collected.extend(batch)
        if len(batch) < page_size:
            break
        start += page_size
        time.sleep(sleep_seconds)
    return collected, complete


def arxiv_lookup_ids(arxiv_ids, sleep_seconds, batch=50):
    """Fetch metadata (categories, comment, dates) for known ids.

    HF gives title/abstract/authors but no arXiv categories, and category
    membership is half of the theme-routing signal.
    """
    found = {}
    ids = [i for i in arxiv_ids if i]
    for i in range(0, len(ids), batch):
        chunk = ids[i : i + batch]
        # arXiv intermittently answers an id_list batch with a well-formed but
        # empty feed, which is not an HTTP error and so does not trip the retry
        # inside arxiv_get. One such batch silently costs 50 papers their
        # categories: a run that resolved 344/344 resolved only 250/343 the
        # next time. An empty batch is always wrong here - these ids came from
        # HF and therefore exist - so retry it once, slowly.
        for attempt in range(2):
            root = arxiv_get({"id_list": ",".join(chunk), "max_results": len(chunk)})
            entries = parse_arxiv_entries(root) if root is not None else []
            if entries:
                for entry in entries:
                    found[entry["arxiv_id"]] = entry
                break
            if attempt == 0:
                warn(f"arXiv returned an empty batch for {len(chunk)} known ids, retrying")
                time.sleep(max(sleep_seconds * 3, 8))
        if i + batch < len(ids):
            time.sleep(sleep_seconds)
    missing = len(ids) - len(found)
    info(f"arXiv id lookup: {len(found)}/{len(ids)} resolved"
         + (f" ({missing} not found)" if missing else ""))
    if ids and missing > len(ids) * 0.1:
        warn(f"{missing} of {len(ids)} HF papers have no arXiv metadata - they keep "
             f"their title/abstract from HF but lose category routing")
    return found


# --------------------------------------------------------------------------
# Code links
# --------------------------------------------------------------------------

RE_GITHUB = re.compile(r"github\.com/([A-Za-z0-9][\w.-]*)/([A-Za-z0-9][\w.-]*)", re.I)
# github.com paths that are not repositories
GITHUB_NON_REPO = {"orgs", "features", "about", "topics", "sponsors", "settings",
                   "marketplace", "collections", "readme", "pricing", "login"}
RE_PROJECT_PAGE = re.compile(r"https?://(?!(?:www\.)?(?:github\.com|arxiv\.org))[\w.-]+\.[a-z]{2,}(?:/[\w./#?=&%+-]*)?", re.I)


def extract_github_repo(*texts):
    """First plausible `owner/name` mentioned in the abstract or comment."""
    for text in texts:
        if not text:
            continue
        for owner, name in RE_GITHUB.findall(text):
            if owner.lower() in GITHUB_NON_REPO:
                continue
            name = re.sub(r"\.git$", "", name).rstrip(".,;:)]}'\"")
            if not name or name.lower() in {"io", "com"}:
                continue
            return f"{owner}/{name}"
    return None


def extract_project_page(*texts):
    for text in texts:
        if not text:
            continue
        m = RE_PROJECT_PAGE.search(text)
        if m:
            return m.group(0).rstrip(".,;:)]}'\"")
    return None


RE_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _normalize_name(text):
    return RE_NON_ALNUM.sub("", (text or "").lower())


def stars_are_the_paper_s(paper):
    """Whether this repo's star count may count as the paper's own popularity.

    A link mined out of an abstract is very often someone ELSE's repo: the
    baseline being compared against, or the base model being built on. Three
    real cases from the first full run - a sparse-attention paper inheriting
    765 stars from the baseline it beats, a video-generation paper inheriting
    2.6k from the backbone it plugs into, and a music model inheriting 10.7k
    from its own previous version. Those stars measure the other project's
    popularity, so counting them fabricates heat.

    The check applies to HF-curated links too, which is the opposite of what
    this code first assumed. Submitters attach the *related* repo just as
    readily: `MassAlloc Attention` carried a link to `flash-sparse-attention`
    (765 stars, the baseline it beats), `YuE2` to `YuE` (10.7k, its own
    previous version), and `LongLive-Plug` to `NVlabs/LongLive` (2.6k, the
    backbone it plugs into). All three were HF-curated and all three would
    have shown a star count that is not theirs.

    So a repo only counts when it is named after the paper (the name before
    the title's colon). That rejects those three and also rejects two honest
    cases - a repo called `object-permanence` for a paper titled "Training
    Object Permanence in World Models", for instance. Under-claiming is the
    right direction to fail: the link still appears in the report, it just
    stops being quoted as this paper's popularity.
    """
    if not paper.get("github_repo"):
        return False
    title = paper.get("title") or ""
    short = title.split(":")[0] if ":" in title else title
    paper_name = _normalize_name(short)
    if len(paper_name) < 3:
        return False
    repo_name = _normalize_name(paper["github_repo"].rstrip("/").split("/")[-1])
    return paper_name in repo_name


def github_stars(full_name):
    """Star count for one repo, or None. Uses GITHUB_TOKEN when present."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    data = fetch_json(f"{GITHUB_API}/repos/{full_name}", headers=headers, retries=2)
    if not data:
        return None
    return data.get("stargazers_count")


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------

def keyword_score(text, keywords):
    """Sum of weights for keywords present, word-boundary matched so 'ar' does
    not fire inside 'architecture' and 'vla' does not fire inside 'vlan'.
    Returns (score, matched_keywords) - the matches go into the output so a bad
    pick can be traced back to the keyword that caused it."""
    score = 0
    matched = []
    for kw, weight in keywords.items():
        if re.search(rf"(?<![a-z0-9]){re.escape(kw.lower())}(?![a-z0-9])", text):
            score += weight
            matched.append(kw)
    return score, matched


def category_score(paper, theme, weights):
    primary = paper.get("primary_category")
    cats = set(paper.get("categories") or [])
    score = 0.0
    if primary and primary in theme.get("primary_categories", []):
        score += weights["category_primary"]
    elif cats & set(theme.get("primary_categories", [])):
        # listed but not primary: worth something, not the full bonus
        score += weights["category_primary"] * 0.5
    score += weights["category_secondary"] * len(cats & set(theme.get("secondary_categories", [])))
    return score


def haystack(paper):
    return " ".join(
        filter(None, [paper.get("title"), paper.get("abstract"), paper.get("comment")])
    ).lower()


def score_paper(paper, theme, weights):
    """Returns (total_score, affinity, breakdown).

    `affinity` is how well the paper matches this theme's subject - keywords
    plus arXiv categories, and deliberately NOT popularity or claim_bonus.
    Ownership is a question of topic; heat only decides the order within a
    chapter.
    """
    kw_raw, matched = keyword_score(haystack(paper), theme["keywords"])
    cat = category_score(paper, theme, weights)
    upvotes = paper.get("hf_upvotes") or 0
    stars = (paper.get("github_stars") or 0) if stars_are_the_paper_s(paper) else 0
    # HF upvotes are scoped to this week; repo stars are a lifetime total. Left
    # uncapped the two mix badly: a 2.7k-star repo with 16 upvotes outranked a
    # 271-upvote paper, i.e. an established project masquerading as this week's
    # heat. The cap keeps stars as corroboration rather than the main signal.
    star_term = min(
        weights["github_star"] * math.log1p(stars),
        weights.get("github_star_cap", 6.0),
    )
    # Upvotes get a gentler curve than the stars do. Under log1p, 271 upvotes
    # sat only 3.4 points above 90 - less than the bonuses for shipping code -
    # so the paper three times as many people upvoted ranked lower. A power
    # curve keeps big numbers distinguishable while still damping the outliers.
    upvote_term = weights["hf_upvote"] * (upvotes ** weights.get("hf_upvote_power", 0.5))
    pop = upvote_term + star_term
    code = weights["has_code"] if paper.get("github_repo") else 0.0
    page = weights["has_project_page"] if paper.get("project_page") else 0.0

    affinity = weights["keyword"] * kw_raw + cat
    # Topic signal decides WHICH chapter a paper belongs to, so it carries full
    # weight in `affinity`. It must not decide the order WITHIN a chapter,
    # where every paper is on-topic by construction: on the first full run a
    # 271-upvote paper ranked below a 90-upvote one purely on keyword count.
    # Hence the discount here - it survives only as a tiebreak among papers
    # with no measured heat at all.
    total = pop + weights.get("keyword_in_rank", 0.25) * affinity + code + page
    breakdown = {
        "keyword_raw": kw_raw,
        "keyword_matched": matched,
        "category": round(cat, 2),
        "popularity": round(pop, 2),
        "stars_counted": stars or None,
        "code_bonus": code,
        "project_page_bonus": page,
    }
    return round(total, 3), round(affinity, 3), breakdown


def route(paper, themes, rank_of, weights, min_affinity, rescue_min, fallback_theme):
    """Decide which single theme owns this paper.

    Eligibility is topical: either the keyword score clears the theme's
    `min_score`, or keywords plus categories together clear `min_affinity`
    (which catches a paper whose arXiv categories say exactly what it is while
    its abstract happens to dodge our keyword lists).

    Among eligible themes the winner is `affinity + claim_bonus`, so the niche
    themes win near-ties instead of being swallowed by llm / vlm.

    A paper eligible nowhere is dropped - UNLESS Hugging Face readers clearly
    care about it, in which case it is routed by arXiv category alone, with
    `fallback_theme` as the catch-all. Routing a keyword-less paper by
    claim_bonus is what put a sparse-attention paper in the smart-glasses
    chapter on the first run; categories are the paper's own declaration of
    what field it is in, so they are the honest tiebreak here.
    """
    scored = {}
    for slug, theme in themes.items():
        total, affinity, breakdown = score_paper(paper, theme, weights)
        scored[slug] = {"total": total, "affinity": affinity, "breakdown": breakdown}

    eligible = [
        slug for slug, s in scored.items()
        if s["breakdown"]["keyword_raw"] >= themes[slug].get("min_score", 3)
        or s["affinity"] >= min_affinity
    ]
    how = "topic"

    if not eligible:
        if (paper.get("hf_upvotes") or 0) < rescue_min:
            return None, None, "no-fit"
        by_cat = sorted(
            scored.items(),
            key=lambda kv: (kv[1]["breakdown"]["category"], -rank_of[kv[0]]),
            reverse=True,
        )
        best_slug, best = by_cat[0]
        eligible = [best_slug if best["breakdown"]["category"] > 0 else fallback_theme]
        how = "hf-rescue"

    winner = max(
        eligible,
        key=lambda slug: (
            scored[slug]["affinity"] + themes[slug].get("claim_bonus", 0.0),
            -rank_of[slug],
        ),
    )
    runner_up = next(
        (
            slug for slug in sorted(
                (s for s in eligible if s != winner),
                key=lambda s: scored[s]["affinity"] + themes[s].get("claim_bonus", 0.0),
                reverse=True,
            )
        ),
        None,
    )
    return winner, {"runner_up": runner_up, "how": how, **scored[winner]}, how


def heat_source(paper):
    """Whether this paper has a measured heat signal the report may cite.

    Only HF upvotes qualify. Stars still nudge the score (capped, and only
    when the repo is the paper's own), but they cannot back a heat claim in
    the prose: they are a lifetime total rather than this week's attention,
    and the report does not print them at all. Letting them set this field
    produced a paper labelled 热度未测得 that was nonetheless eligible for the
    top-5 block - the label and the gate have to mean the same thing.
    """
    return "hf" if (paper.get("hf_upvotes") or 0) > 0 else "none"


def heat_label(paper):
    """The exact string the report prints for this paper's heat.

    Computed here rather than described to the agent that writes the prose,
    because this is the one line in the report that must not be improvised -
    an invented or inflated number is the failure mode this whole project has
    to avoid.

    Star counts are deliberately NOT printed. Even an HF-curated link is
    routinely the baseline, the backbone or the paper's own previous version,
    and `LongLive-Plug` pointing at `LongLive` cannot be told apart from a
    legitimate link by any rule this script could apply. A count that might be
    someone else's is worse than no count, so the report says only that code
    exists and links it - the reader can see the stars themselves.
    """
    upvotes = paper.get("hf_upvotes") or 0
    parts = [f"🔥 HF {upvotes} 赞"] if upvotes > 0 else ["热度未测得"]
    repo = paper.get("github_repo")
    if repo:
        parts.append(f"💻 [代码]({repo})")
    return " ｜ ".join(parts)


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

def load_config():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    shared = {k: v for k, v in config.get("shared", {}).items() if not k.startswith("_")}
    themes = {}
    for slug, raw in config["themes"].items():
        merged = dict(shared)
        merged.update({k: v for k, v in raw.items() if not k.startswith("_")})
        merged["slug"] = slug
        themes[slug] = merged
    order = shared.get("claim_order") or list(themes)
    # any theme missing from claim_order still has to be orderable
    order = [s for s in order if s in themes] + [s for s in themes if s not in order]
    return shared, themes, order


def is_excluded(title, patterns):
    low = (title or "").lower()
    return any(re.search(p, low) for p in patterns)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--theme", help="only collect this theme (debugging); default is all")
    ap.add_argument("--list-themes", action="store_true", help="print theme slugs and exit")
    ap.add_argument("--outdir", help="write <slug>.json per theme into this directory")
    ap.add_argument("--week-of", help="YYYY-MM-DD anchor (window is the 7 days up to it; default today)")
    ap.add_argument("--emit", type=int, help="papers to emit per theme (default: config 'emit')")
    ap.add_argument("--enrich-pool", type=int, help="candidates per theme to look up GitHub stars for")
    ap.add_argument("--max-results", type=int, help="override arxiv_max_results_per_query")
    ap.add_argument("--no-github", action="store_true", help="skip GitHub star lookups")
    ap.add_argument(
        "--no-arxiv",
        action="store_true",
        help="skip every arXiv call and build from Hugging Face alone. A degraded "
        "mode for when arXiv is throttling or down: the HF-only pool still covers "
        "llm / vlm / agent well but leaves robotics and wearable-xr thin, and no "
        "paper gets arXiv categories, so routing falls back to keywords only.",
    )
    ap.add_argument("--quiet-stdout", action="store_true", help="do not echo the payload to stdout")
    ap.add_argument(
        "--rescore",
        metavar="DIR",
        help="recompute scores, heat labels and ordering for the <slug>.json files "
        "already in DIR, then rewrite them in place. No network at all. Use this "
        "after changing weights in topics.json so a retune does not cost another "
        "full fetch - and remember arXiv throttles hard if you refetch repeatedly.",
    )
    args = ap.parse_args()

    shared, themes, claim_order = load_config()

    if args.list_themes:
        for slug in claim_order:
            print(f"{slug}\t{themes[slug].get('title', '')}")
        return

    if args.theme and args.theme not in themes:
        sys.exit(f"unknown theme '{args.theme}'; config has: {', '.join(themes)}")
    wanted = [args.theme] if args.theme else claim_order

    if args.rescore:
        rescore(Path(args.rescore), themes, shared, wanted)
        return

    weights = shared["weights"]
    excludes = shared.get("exclude_title_patterns", [])
    sleep_seconds = shared.get("arxiv_sleep_seconds", 3.0)
    max_results = args.max_results or shared.get("arxiv_max_results_per_query", 150)
    rescue_min = shared.get("hf_rescue_min_upvotes", 20)
    min_affinity = shared.get("min_affinity", 4.0)
    fallback_theme = shared.get("fallback_theme", "deep-learning")
    if fallback_theme not in themes:
        sys.exit(f"shared.fallback_theme '{fallback_theme}' is not a configured theme")

    anchor = (
        datetime.strptime(args.week_of, "%Y-%m-%d").date()
        if args.week_of
        else datetime.now(timezone.utc).date()
    )
    start_date = anchor - timedelta(days=6)
    info(f"window {start_date} .. {anchor} | themes: {', '.join(wanted)}")
    if not TOKEN and not args.no_github:
        info("no GITHUB_TOKEN set - star lookups run unauthenticated (60 req/hr)")

    # ---------------- collect ----------------
    candidates = {}

    def absorb(paper, source):
        """Merge one paper into the pool. HF fields win over arXiv-only ones."""
        existing = candidates.get(paper["arxiv_id"])
        if existing is None:
            paper["sources"] = [source]
            candidates[paper["arxiv_id"]] = paper
            return
        if source not in existing["sources"]:
            existing["sources"].append(source)
        for key, value in paper.items():
            if key in ("sources",):
                continue
            if value in (None, "", []) :
                continue
            if existing.get(key) in (None, "", []):
                existing[key] = value

    hf_papers = fetch_hf_window(start_date, anchor)
    if hf_papers:
        hf_meta = {} if args.no_arxiv else arxiv_lookup_ids(list(hf_papers), sleep_seconds)
        for arxiv_id, paper in hf_papers.items():
            merged = dict(hf_meta.get(arxiv_id) or {})
            merged.update({k: v for k, v in paper.items() if v not in (None, "", [])})
            merged.setdefault("abs_url", f"https://arxiv.org/abs/{arxiv_id}")
            merged.setdefault("pdf_url", f"https://arxiv.org/pdf/{arxiv_id}")
            absorb(merged, "hf")

    incomplete_themes = set()
    if args.no_arxiv:
        warn("--no-arxiv: building from Hugging Face alone. Every theme is marked "
             "incomplete, and robotics / wearable-xr will be thin.")
        incomplete_themes.update(wanted)
    for slug in [] if args.no_arxiv else wanted:
        theme = themes[slug]
        info(f"arXiv queries for '{slug}' ({theme.get('title', slug)})")
        for query_spec in theme.get("arxiv_queries", []):
            query = build_query(query_spec["cats"], query_spec["terms"], start_date, anchor)
            before = len(candidates)
            papers, complete = fetch_arxiv_query(query, max_results, sleep_seconds)
            for paper in papers:
                absorb(paper, "arxiv")
            if not complete:
                incomplete_themes.add(slug)
            info(f"  +{len(candidates) - before} new (pool now {len(candidates)})"
                 + ("  [PARTIAL - a page could not be fetched]" if not complete else ""))
            time.sleep(sleep_seconds)

    if incomplete_themes:
        warn(f"arXiv data is incomplete for: {', '.join(sorted(incomplete_themes))} "
             f"- those chapters are built on partial candidates")

    info(f"{len(candidates)} unique papers in the pool")

    # ---------------- derive code / page links ----------------
    for paper in candidates.values():
        if not paper.get("github_repo"):
            repo = extract_github_repo(paper.get("comment"), paper.get("abstract"))
            if repo:
                paper["github_repo"] = f"https://github.com/{repo}"
                paper["github_repo_source"] = "abstract"
        if not paper.get("project_page"):
            paper["project_page"] = extract_project_page(paper.get("comment"))

    # ---------------- assign each paper to exactly one theme ----------------
    # fit = keyword + category + claim_bonus, popularity excluded on purpose.
    # Ties break on claim_order, which puts the niche themes first so a
    # cross-over paper does not get swallowed by llm / vlm.
    rank_of = {slug: i for i, slug in enumerate(claim_order)}
    assigned = {slug: [] for slug in themes}
    dropped_excluded = 0
    dropped_nofit = 0
    rescued = 0

    for paper in candidates.values():
        if is_excluded(paper.get("title"), excludes):
            dropped_excluded += 1
            continue
        slug, detail, how = route(
            paper, themes, rank_of, weights, min_affinity, rescue_min, fallback_theme
        )
        if slug is None:
            dropped_nofit += 1
            continue
        if how == "hf-rescue":
            rescued += 1
            info(f"  rescued by HF upvotes ({paper.get('hf_upvotes')}), routed on "
                 f"arXiv category -> {slug}: {paper['title'][:60]}")
        paper = dict(paper)
        paper.update(
            {
                "theme": slug,
                "fit": detail["affinity"],
                "alt_theme": detail["runner_up"],
                "routed_by": detail["how"],
                "score": detail["total"],
                "score_breakdown": detail["breakdown"],
            }
        )
        assigned[slug].append(paper)

    info(f"assigned: " + ", ".join(f"{s}={len(assigned[s])}" for s in claim_order))
    info(f"dropped: {dropped_excluded} by title pattern, {dropped_nofit} below min_score"
         + (f"; {rescued} rescued by HF upvotes" if rescued else ""))

    # ---------------- enrich the top of each theme with GitHub stars ----------------
    # Stars are looked up only for the papers that could plausibly make the cut,
    # because every lookup costs one GitHub API call.
    if not args.no_github:
        star_cache = {}
        for slug in wanted:
            pool_size = args.enrich_pool or themes[slug].get("enrich_pool", 30)
            pool = sorted(assigned[slug], key=lambda p: p["score"], reverse=True)[:pool_size]
            # Only look up repos whose stars may count as the paper's own.
            # Skipping the rest saves API quota and, more importantly, keeps an
            # inherited star count out of the JSON where the report writer
            # would quote it as this paper's.
            targets = [
                p for p in pool
                if p.get("github_stars") is None and stars_are_the_paper_s(p)
            ]
            if not targets:
                continue
            info(f"looking up {len(targets)} GitHub repos for '{slug}'")
            for paper in targets:
                full_name = "/".join(paper["github_repo"].rstrip("/").split("/")[-2:])
                if full_name not in star_cache:
                    star_cache[full_name] = github_stars(full_name)
                paper["github_stars"] = star_cache[full_name]
            # re-score now that stars are known
            theme = themes[slug]
            for paper in pool:
                total, fit, breakdown = score_paper(paper, theme, weights)
                paper["score"], paper["score_breakdown"] = total, breakdown

    # ---------------- emit ----------------
    generated_at = datetime.now(timezone.utc).isoformat()
    thin = []
    payloads = {}

    for slug in wanted:
        theme = themes[slug]
        emit = args.emit or theme.get("emit", 25)
        papers = sorted(assigned[slug], key=lambda p: (p["score"], p["fit"]), reverse=True)[:emit]
        for paper in papers:
            paper["heat_source"] = heat_source(paper)
            paper["heat_label"] = heat_label(paper)
            paper["authors_display"] = _authors_display(paper.get("authors") or [])

        measured = sum(1 for p in papers if p["heat_source"] != "none")
        payloads[slug] = {
            "generated_at": generated_at,
            "theme": slug,
            "theme_title": theme.get("title", slug),
            "theme_subtitle": theme.get("subtitle", ""),
            "accent": theme.get("accent"),
            "week_start": start_date.isoformat(),
            "week_end": anchor.isoformat(),
            "pick": theme.get("pick", 10),
            "authenticated_github": bool(TOKEN) and not args.no_github,
            "arxiv_data_complete": slug not in incomplete_themes,
            "candidate_count": len(assigned[slug]),
            "measured_heat_count": measured,
            "papers": papers,
        }
        info(f"{slug}: emitting {len(papers)} of {len(assigned[slug])} "
             f"({measured} with measured heat)")
        if len(papers) < theme.get("min_papers", 5):
            thin.append(f"{slug} ({len(papers)})")

        if args.outdir:
            out_path = Path(args.outdir)
            if not out_path.is_absolute():
                out_path = ROOT / out_path
            out_path.mkdir(parents=True, exist_ok=True)
            target = out_path / f"{slug}.json"
            target.write_text(
                json.dumps(payloads[slug], indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            info(f"wrote {target}")

    if not args.quiet_stdout:
        print(json.dumps(payloads if len(payloads) > 1 else next(iter(payloads.values())),
                         indent=2, ensure_ascii=False))

    # A theme that collected almost nothing means the queries or the filters
    # broke, not that the field went quiet. Exit non-zero so a scheduled run can
    # tell the two apart instead of silently publishing an empty chapter.
    if thin:
        warn(f"below min_papers: {', '.join(thin)} - treating this run as degraded")
        sys.exit(2)


def rescore(outdir, themes, shared, wanted):
    """Recompute scores and labels for already-fetched JSON, in place.

    Theme ownership is NOT revisited: it depends on keywords and categories,
    neither of which a weight change touches, and re-routing would need the
    whole cross-theme pool rather than six already-trimmed top-25 lists.
    """
    if not outdir.is_absolute():
        outdir = ROOT / outdir
    weights = shared["weights"]
    for slug in wanted:
        path = outdir / f"{slug}.json"
        if not path.exists():
            warn(f"no {path} to rescore")
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        papers = payload.get("papers", [])
        for paper in papers:
            total, affinity, breakdown = score_paper(paper, themes[slug], weights)
            paper["score"], paper["fit"], paper["score_breakdown"] = total, affinity, breakdown
            paper["heat_source"] = heat_source(paper)
            paper["heat_label"] = heat_label(paper)
        papers.sort(key=lambda p: (p["score"], p["fit"]), reverse=True)
        payload["measured_heat_count"] = sum(1 for p in papers if p["heat_source"] != "none")
        payload["rescored_at"] = datetime.now(timezone.utc).isoformat()
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        info(f"rescored {path} ({len(papers)} papers, "
             f"{payload['measured_heat_count']} with measured heat)")


def _authors_display(authors, cap=6):
    if not authors:
        return ""
    if len(authors) <= cap:
        return ", ".join(authors)
    return ", ".join(authors[:cap]) + f" 等 {len(authors)} 人"


if __name__ == "__main__":
    main()
