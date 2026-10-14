#!/bin/sh
# Fresh-clone check inside docker:27-dind. /src = repo (read-only), /env.txt = endpoint values.
set -u
export DOCKER_HOST=unix:///var/run/docker.sock
unset DOCKER_TLS_CERTDIR
(dockerd >/tmp/dockerd.log 2>&1 &)
for i in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 1; done
apk add --no-cache git make curl python3 >/dev/null 2>&1
echo "Fresh-clone check: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
git config --global --add safe.directory '*'
git clone -q /src /work && cd /work
echo "commit: $(git log -1 --format='%h %s')"
echo "host: $(uname -srm); $(. /etc/os-release; echo $PRETTY_NAME); $(docker --version); $(docker compose version); $(make --version | head -1)"
echo "untracked files after clone: $(git status --porcelain | wc -l)"
echo "data/ tracked size: $(du -sh track_2b/data | cut -f1)"
echo
echo "=== 1. make test (from repo root) ==="
make test 2>&1 | grep -E "passed|failed|error" | tail -2
echo
echo "=== 2. make run (from repo root), endpoint from track_2b/.env, no local llama-server ==="
cp track_2b/.env.example track_2b/.env
grep -E '^LLM_(BASE_URL|API_KEY|NAME)=' /env.txt >> track_2b/.env
(make run >/tmp/run.log 2>&1 &)
for i in $(seq 1 600); do curl -sf http://127.0.0.1:8000/v1/health >/tmp/health.json 2>/dev/null && break; sleep 2; done
echo "health after ${i} polls: $(cat /tmp/health.json)"
python3 - <<'EOF'
import json, urllib.request
msg = json.loads(open("/work/track_2b/data/seed/messages.seed.jsonl", encoding="utf-8").readline())
body = {k: msg.get(k) for k in ("message_id", "subject", "body", "sender", "channel", "received_at")}
req = urllib.request.Request("http://127.0.0.1:8000/v1/triage", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
r = json.loads(urllib.request.urlopen(req, timeout=600).read())
res = r.get("result", r)
print("triage", msg["message_id"], {k: res.get(k) for k in ("route", "deadline", "assignee", "safety_flag", "abstain")})
print("gold   ", {k: msg["label"].get(k) for k in ("route", "deadline", "assignee", "safety_flag")})
print("evidence:", res.get("evidence"))
EOF
echo "web UI: HTTP $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/)"
cd /work/track_2b && docker compose down >/dev/null 2>&1
echo
echo "=== 3. make run WITHOUT track_2b/.env (no credentials) ==="
mv /work/track_2b/.env /tmp/env.bak
cd /work
(make run >/tmp/run2.log 2>&1 &)
for i in $(seq 1 300); do curl -sf http://127.0.0.1:8000/v1/health >/tmp/health2.json 2>/dev/null && break; sleep 2; done
echo "health: $(cat /tmp/health2.json)"
echo "load seed (without stored predictions): $(curl -s -X POST 'http://127.0.0.1:8000/v1/inbox/load/seed')"
echo "sort without endpoint: $(curl -s -X POST http://127.0.0.1:8000/v1/inbox/sort)"
echo "triage without endpoint: $(curl -s -o /tmp/t.json -w "HTTP %{http_code}" -X POST -H "Content-Type: application/json" --data @/s/body.json http://127.0.0.1:8000/v1/triage) $(cat /tmp/t.json)"
python3 /s/inbox_count.py
echo "web UI: HTTP $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/)"
cd /work/track_2b && docker compose down >/dev/null 2>&1
echo "done $(date -u '+%H:%M:%S UTC')"
