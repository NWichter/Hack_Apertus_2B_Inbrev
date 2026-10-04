"""Pick a fixed, stratified subset of a gold file: every safety case, then routes round-robin."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("gold", type=Path)
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    rows = [json.loads(x) for x in a.gold.read_text(encoding="utf-8").splitlines() if x.strip()]
    rng = random.Random(a.seed)
    pick = [r for r in rows if r["label"]["safety_flag"]]
    by_route = defaultdict(list)
    for r in rows:
        if not r["label"]["safety_flag"]:
            by_route[r["label"]["route"]].append(r)
    for v in by_route.values():
        rng.shuffle(v)
    routes = sorted(by_route)
    while len(pick) < a.n and any(by_route.values()):
        for route in routes:
            if by_route[route] and len(pick) < a.n:
                pick.append(by_route[route].pop())
    pick.sort(key=lambda r: r["message_id"])
    a.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in pick), encoding="utf-8")
    print(json.dumps({"n": len(pick), "safety": sum(r["label"]["safety_flag"] for r in pick), "out": str(a.out)}))


if __name__ == "__main__":
    main()
