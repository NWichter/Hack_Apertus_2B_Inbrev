#!/usr/bin/env bash
# IMAP import against a local test mail server (GreenMail) on an internal Docker network.
# No host ports, no internet. Sends three seed messages over SMTP, then reads them with
# `inbrev fetch-imap`: read-only twice (same result), then with --mark-seen, then again (0 new).
#   bash scripts/imap_check.sh [OUT_DIR]
set -euo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
OUT="${1:-runs/imap}"
mkdir -p "$OUT"
NET=inbrev-mailtest
GM=inbrev-greenmail
GM_IMAGE=greenmail/standalone:2.1.2@sha256:572d22796908375678119a13fabfcdc5416c9003404ab975fe824692fe02ba03
cleanup() { docker rm -f "$GM" >/dev/null 2>&1 || true; docker network rm "$NET" >/dev/null 2>&1 || true; }
trap cleanup EXIT
cleanup
IMAGE="${IMAGE:-inbrev:latest}"
docker build -q -t "$IMAGE" . >/dev/null

{
  echo "Inbrev IMAP import check, $(date -u +'%Y-%m-%d %H:%M:%S UTC'), git $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  docker network create --internal "$NET" >/dev/null
  docker run -d --name "$GM" --network "$NET" \
    -e GREENMAIL_OPTS="-Dgreenmail.setup.test.smtp -Dgreenmail.setup.test.imap -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.users=praxis:test-only@praxis.example -Dgreenmail.verbose=false" \
    "$GM_IMAGE" >/dev/null
  echo "mail server: $GM_IMAGE on network $NET (internal: $(docker network inspect -f '{{.Internal}}' "$NET"))"
  R=(docker run --rm --network "$NET" -e INBREV_IMAP_PASSWORD=test-only "$IMAGE")
  docker run --rm -i --network "$NET" "$IMAGE" python - <<'PY'
import json, smtplib, time
from email.message import EmailMessage
from email.utils import format_datetime
from datetime import datetime
seed = [json.loads(l) for l in open("data/seed/messages.seed.jsonl", encoding="utf-8")][:3]
for _ in range(60):
    try:
        s = smtplib.SMTP("inbrev-greenmail", 3025, timeout=5); break
    except OSError:
        time.sleep(1)
for m in seed:
    e = EmailMessage()
    e["From"] = m.get("sender") or "absender@mail.example"
    e["To"] = "praxis@praxis.example"
    e["Subject"] = m.get("subject") or ""
    e["Date"] = format_datetime(datetime.fromisoformat(m.get("received_at") or "2026-10-05T08:15").astimezone())
    e.set_content(m.get("body") or "")
    s.send_message(e)
    print("sent:", m["message_id"], "|", e["From"], "|", e["Subject"])
s.quit()
PY
  F=(python -m inbrev fetch-imap --host inbrev-greenmail --port 3143 --security plain --user praxis)
  echo "--- fetch 1 (unseen, read-only)"
  "${R[@]}" sh -c "${F[*]} --out /tmp/a.jsonl && python -c \"import json; [print(m['message_id'], m['channel'], m['received_at'], '|', m['subject']) for m in map(json.loads, open('/tmp/a.jsonl', encoding='utf-8'))]\""
  echo "--- fetch 2 (unseen, read-only: same messages again)"
  "${R[@]}" ${F[*]} --out /tmp/b.jsonl
  echo "--- fetch 3 (--mark-seen)"
  "${R[@]}" ${F[*]} --mark-seen --out /tmp/c.jsonl
  echo "--- fetch 4 (unseen: nothing new)"
  "${R[@]}" ${F[*]} --out /tmp/d.jsonl
  echo "--- wrong password (must fail)"
  docker run --rm --network "$NET" -e INBREV_IMAP_PASSWORD=wrong "$IMAGE" ${F[*]} --out /tmp/e.jsonl 2>&1 | tail -1 || true
} 2>&1 | tee "$OUT/imap-check.log"
