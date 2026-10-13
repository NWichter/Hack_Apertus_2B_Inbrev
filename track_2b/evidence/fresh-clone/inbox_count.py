import json
import urllib.request

d = json.loads(urllib.request.urlopen("http://127.0.0.1:8000/v1/inbox").read())
items = d.get("items", [])
print(
    "inbox items:", len(items),
    "with stored result:", sum(1 for x in items if x.get("result")),
    "taken out of automation (flag or abstain):",
    sum(1 for x in items if (x.get("result") or {}).get("safety_flag") or (x.get("result") or {}).get("abstain")),
)
