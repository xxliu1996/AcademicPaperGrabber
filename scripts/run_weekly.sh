#!/bin/bash
# Weekly runner for launchd. Invokes Claude Code headlessly on /papers-weekly.
#
# launchd starts jobs with a near-empty environment and no login shell, so
# everything the run needs - PATH, the repo location, credentials - has to be
# set up explicitly here rather than inherited.

set -uo pipefail

# Resolve the repo from this script's own location, so moving the checkout
# (CluadeProjects -> xxliu1996_githubrepos) needs no edit here.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE="/Users/xingxingliu/.local/bin/claude"
LOG_DIR="$ROOT/logs"
DATE="$(date +%F)"
LOG="$LOG_DIR/$DATE.log"
START_EPOCH="$(date +%s)"

mkdir -p "$LOG_DIR"

# git needs to find its credential helper and the system binaries
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:$HOME/.local/bin"

# claude reads its login token from the "Claude Code-credentials" keychain item,
# and the keychain lookup needs USER/LOGNAME set. Without these the run dies
# with "Not logged in - Please run /login".
export HOME="${HOME:-/Users/xingxingliu}"
export USER="${USER:-xingxingliu}"
export LOGNAME="${LOGNAME:-$USER}"
export SHELL="${SHELL:-/bin/zsh}"

{
  echo "==================== $(date '+%F %T %Z') ===================="
  echo "runner  : $0"
  echo "root    : $ROOT"
  echo "claude  : $($CLAUDE --version 2>&1)"

  # Raises the GitHub API ceiling from 60/hr to 5000/hr, used for the star
  # lookups on papers that ship code. Read straight from the keychain so no
  # plaintext token ever lands on disk. Optional: without it the run still
  # works, it just backs off.
  GITHUB_TOKEN="$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill 2>/dev/null | sed -n 's/^password=//p')"
  if [ -n "$GITHUB_TOKEN" ]; then
    export GITHUB_TOKEN
    echo "token   : loaded from keychain (${#GITHUB_TOKEN} chars)"
  else
    echo "token   : none - anonymous, expect rate-limit backoff"
  fi

  cd "$ROOT" || { echo "FATAL: cannot cd to $ROOT"; exit 1; }

  # Pull first so a report written on another machine does not cause a conflict
  # when this run tries to push. A rebase refuses to start with a dirty tree, so
  # set uncommitted work aside first - including untracked files, which is where
  # a half-finished report would live.
  STASHED=0
  if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
    if git stash push -u -q -m "run_weekly auto-stash $(date +%FT%T)"; then
      STASHED=1
      echo "stash   : local changes set aside"
    else
      echo "WARN: git stash failed, skipping pull to avoid touching your working tree"
    fi
  fi

  if [ "$STASHED" -eq 1 ] || git diff --quiet; then
    git pull --rebase --quiet origin main 2>&1 || echo "WARN: git pull failed, continuing"
  fi

  if [ "$STASHED" -eq 1 ]; then
    if git stash pop -q 2>&1; then
      echo "stash   : local changes restored"
    else
      # Never silently discard the user's work - leave it in the stash list and
      # make the failure loud.
      echo "WARN: could not restore stashed changes (conflict). They are SAFE in the stash:"
      git stash list | head -3
    fi
  fi

  echo "--- running /papers-weekly ---"
  "$CLAUDE" -p "/papers-weekly" \
    --permission-mode acceptEdits \
    --allowedTools "Bash,Read,Write,Edit,Glob,Grep,Agent,TodoWrite" \
    2>&1
  STATUS=$?

  echo "--- claude exited with $STATUS ---"

  # Checking that the file merely exists is not enough: a re-run on a date that
  # already has a report will happily exit 0 without regenerating anything.
  # Require it to have been written during THIS run.
  REPORT="$ROOT/reports/$DATE/report.md"
  if [ ! -f "$REPORT" ]; then
    echo "FAILED: $REPORT was never written"
    STATUS=1
  elif [ "$(stat -f %m "$REPORT")" -lt "$START_EPOCH" ]; then
    echo "FAILED: $REPORT is stale (not rewritten this run)"
    STATUS=1
  else
    PAPERS="$(grep -c '^### [0-9]' "$REPORT" 2>/dev/null || echo 0)"
    CHAPTERS="$(grep -c '^## [一二三四五六]、' "$REPORT" 2>/dev/null || echo 0)"
    echo "ok: report.md ($(wc -c < "$REPORT" | tr -d ' ') bytes, $CHAPTERS chapters, $PAPERS papers)"
    # Six chapters of ten is the target; a run that produced almost nothing
    # parsed wrong or the fetch failed, and must not pass as a success.
    if [ "$PAPERS" -lt 20 ]; then
      echo "FAILED: only $PAPERS papers written - expected ~60"
      STATUS=1
    fi
  fi

  # The site is the deliverable, so rebuild it here too rather than trusting the
  # model to have run step 5. Idempotent, so a second build is harmless.
  if ! python3 "$ROOT/scripts/build_site.py"; then
    echo "FAILED: build_site.py could not rebuild docs/"
    STATUS=1
  fi

  # ---------------------------------------------------------------------------
  # Optional email digest.
  #
  # Off until you put a Gmail app password in the keychain yourself:
  #
  #   security add-generic-password -a "$USER" -s AcademicPaperGrabber-smtp \
  #            -w '<16-char app password from myaccount.google.com/apppasswords>'
  #
  # Nothing here ever writes the password to disk or to the log. Without the
  # keychain item the run just skips this block.
  # ---------------------------------------------------------------------------
  SMTP_PASS="$(security find-generic-password -a "$USER" -s AcademicPaperGrabber-smtp -w 2>/dev/null)"
  if [ -n "$SMTP_PASS" ] && [ "$STATUS" -eq 0 ]; then
    if SMTP_PASS="$SMTP_PASS" python3 "$ROOT/scripts/send_email.py" --date "$DATE"; then
      echo "email   : sent"
    else
      # A failed notification must not fail the week's report.
      echo "WARN: email digest failed to send"
    fi
  else
    [ -z "$SMTP_PASS" ] && echo "email   : skipped (no AcademicPaperGrabber-smtp keychain item)"
  fi

  # Surface the outcome in Notification Center so a silent failure is visible
  # without having to open the log.
  if [ "$STATUS" -eq 0 ]; then
    osascript -e "display notification \"论文周报已生成：reports/$DATE\" with title \"AcademicPaperGrabber\"" 2>/dev/null
  else
    osascript -e "display notification \"运行失败（退出码 $STATUS），见 logs/$DATE.log\" with title \"AcademicPaperGrabber\" sound name \"Basso\"" 2>/dev/null
  fi

  echo "==================== done: $(date '+%F %T %Z') ===================="
  exit "$STATUS"
} 2>&1 | tee -a "$LOG"

exit "${PIPESTATUS[0]}"
