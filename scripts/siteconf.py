#!/usr/bin/env python3
"""Where this checkout's settings come from, so nothing is hardcoded to one person.

Resolution order for every setting: environment variable, then
`config/local.json` (gitignored), then a sensible default. The site URL has a
fourth source that usually makes configuration unnecessary: it is derived from
the `origin` git remote, because a GitHub Pages URL is a pure function of the
owner and repository name.

Run this file directly to see what the current checkout resolves to.
"""

import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_CONFIG = ROOT / "config" / "local.json"

DEFAULTS = {
    "site_title": "AI 论文周报",
    "site_tagline": "每周自动抓取六个方向最近一周的热门论文，每个方向 10 篇，人读的那种周报。",
    "site_url": "",
    "mail_from": "",
    "mail_to": "",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 465,
    "keychain_service": "AcademicPaperGrabber-smtp",
}

# config key -> environment variable
ENV_KEYS = {
    "site_title": "PAPERS_SITE_TITLE",
    "site_tagline": "PAPERS_SITE_TAGLINE",
    "site_url": "PAPERS_SITE_URL",
    "mail_from": "PAPERS_MAIL_FROM",
    "mail_to": "PAPERS_MAIL_TO",
    "smtp_host": "PAPERS_SMTP_HOST",
    "smtp_port": "PAPERS_SMTP_PORT",
    "keychain_service": "PAPERS_KEYCHAIN_SERVICE",
}

_RE_REMOTE = re.compile(
    r"^(?:https?://[^/]+/|git@[^:]+:|ssh://git@[^/]+/)(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$"
)


def _from_file():
    if not LOCAL_CONFIG.exists():
        return {}
    try:
        data = json.loads(LOCAL_CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {k: v for k, v in data.items() if not k.startswith("_")}


def derive_site_url():
    """`https://<owner>.github.io/<repo>` from the origin remote, or ''.

    GitHub Pages for a project repo always lives at that address, so a fresh
    clone needs no configuration at all. A `<owner>.github.io` repo is the
    user/organisation site and serves from the domain root instead.
    """
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT, capture_output=True, text=True, timeout=10, check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    m = _RE_REMOTE.match(url)
    if not m:
        return ""
    owner, repo = m.group("owner"), m.group("repo")
    if repo.lower() == f"{owner.lower()}.github.io":
        return f"https://{repo}"
    return f"https://{owner}.github.io/{repo}"


def load():
    """Every setting, resolved. `site_url` has no trailing slash."""
    conf = dict(DEFAULTS)
    conf.update(_from_file())
    for key, env in ENV_KEYS.items():
        value = os.environ.get(env, "").strip()
        if value:
            conf[key] = value
    if not conf["site_url"]:
        conf["site_url"] = derive_site_url()
    conf["site_url"] = str(conf["site_url"]).rstrip("/")
    try:
        conf["smtp_port"] = int(conf["smtp_port"])
    except (TypeError, ValueError):
        conf["smtp_port"] = DEFAULTS["smtp_port"]
    return conf


if __name__ == "__main__":
    for key, value in sorted(load().items()):
        shown = value if value != "" else "(unset)"
        print(f"{key:18} {shown}")
