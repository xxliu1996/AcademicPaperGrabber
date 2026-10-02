#!/usr/bin/env python3
"""Mail one week's digest to yourself over Gmail SMTP.

Called by run_weekly.sh, which is the only place the credential is handled: it
reads a Gmail app password out of the macOS keychain and passes it in the
SMTP_PASS environment variable. This script never writes the password anywhere
and never falls back to prompting - if SMTP_PASS is absent it exits 0 having
done nothing, so a missing keychain item can never fail the weekly run.

Set it up once:

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

ROOT = Path(__file__).resolve().parent.parent

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
MAIL_FROM = "wakeupliu1996@gmail.com"
MAIL_TO = "wakeupliu1996@gmail.com"
SITE_URL = "https://xxliu1996.github.io/AcademicPaperGrabber"


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
    ap.add_argument("--dry-run", action="store_true", help="print the mail instead of sending")
    args = ap.parse_args()

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
    msg["From"] = MAIL_FROM
    msg["To"] = args.to
    msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    msg.set_content(build_body(args.date, md))

    if args.dry_run:
        print(msg)
        return

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
        smtp.login(MAIL_FROM, password)
        smtp.send_message(msg)
    info(f"sent {args.date} digest to {args.to}")


if __name__ == "__main__":
    main()
