#!/usr/bin/env python3
"""Mail one week's digest to yourself over SMTP. Optional and off by default.

Addresses are never hardcoded: they come from PAPERS_MAIL_FROM /
PAPERS_MAIL_TO or config/local.json (see scripts/siteconf.py). With no address
configured this exits 0 having done nothing, so a fresh clone is not expected
to carry anyone's email.

The credential is handled only by run_weekly.sh, which reads it out of the
macOS keychain and passes it in the SMTP_PASS environment variable. This
script never writes the password anywhere and never prompts; without
SMTP_PASS it also exits 0, so a missing keychain item cannot fail the weekly
run.

Set it up once (Gmail example):

    security add-generic-password -a "$USER" -s AcademicPaperGrabber-smtp \\
             -w '<16-char app password from myaccount.google.com/apppasswords>'

A normal Google account password will NOT work; Gmail requires an app password
for SMTP.
"""

import argparse
import json
import os
import re
import smtplib
import sys
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import siteconf  # noqa: E402  - needs the path line above

ROOT = Path(__file__).resolve().parent.parent

_CONF = siteconf.load()
SMTP_HOST = _CONF["smtp_host"]
SMTP_PORT = _CONF["smtp_port"]
MAIL_FROM = _CONF["mail_from"]
MAIL_TO = _CONF["mail_to"]
SITE_URL = _CONF["site_url"]


def info(msg):
    print(f"[mail] {msg}", file=sys.stderr)


def build_body(date_str, md):
    """Plain text: the lede, the top-5 block, and a per-chapter paper list.

    Deliberately not the whole report - the mail is a nudge to go read the site,
    not a replacement for it.
    """
    lines = md.splitlines()
    out = [f"AI 论文周报 {date_str}", f"{SITE_URL}/r/{date_str}.html", ""]

    # everything from the H1 to the first '---' is the lede
    lede = []
    for line in lines[1:]:
        if line.strip().startswith("---"):
            break
        if line.strip() and not line.startswith("#"):
            lede.append(line.strip())
    if lede:
        out.extend(["【本周导语】", *lede, ""])

    mode = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            heading = stripped[3:].strip()
            mode = "top" if heading.startswith("⭐") else "chapter"
            out.extend(["", f"【{heading}】"])
            continue
        if mode == "top" and re.match(r"^\d+\.", stripped):
            out.append(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 <\2>", stripped))
            continue
        m = re.match(r"^###\s+(\d+\..*)$", stripped)
        if m and mode == "chapter":
            out.append(f"  {m.group(1)}")

    out.extend(["", "—", f"全文：{SITE_URL}/r/{date_str}.html", f"归档：{SITE_URL}/"])
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD of the report to send")
    ap.add_argument("--to", default=MAIL_TO)
    ap.add_argument("--from", dest="mail_from", default=MAIL_FROM)
    ap.add_argument("--dry-run", action="store_true", help="print the mail instead of sending")
    args = ap.parse_args()

    if not args.mail_from or not args.to:
        info("no mail_from/mail_to configured (PAPERS_MAIL_FROM / PAPERS_MAIL_TO or "
             "config/local.json) - skipping (this is not an error)")
        return

    password = os.environ.get("SMTP_PASS", "").strip()
    if not password and not args.dry_run:
        info("SMTP_PASS not set - skipping (this is not an error)")
        return

    report = ROOT / "reports" / args.date / "report.md"
    if not report.exists():
        sys.exit(f"no report at {report}")
    md = report.read_text(encoding="utf-8")

    counts = ""
    index = ROOT / "docs" / "data" / "reports.json"
    if index.exists():
        try:
            for rec in json.loads(index.read_text(encoding="utf-8")):
                if rec.get("date") == args.date:
                    counts = f"（{rec.get('count', 0)} 篇）"
                    break
        except json.JSONDecodeError:
            pass

    msg = EmailMessage()
    msg["Subject"] = f"AI 论文周报 {args.date}{counts}"
    msg["From"] = args.mail_from
    msg["To"] = args.to
    msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    msg.set_content(build_body(args.date, md))

    if args.dry_run:
        print(msg)
        return

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.login(args.mail_from, password)
        smtp.send_message(msg)
    info(f"sent {args.date} digest to {args.to}")


if __name__ == "__main__":
    main()
