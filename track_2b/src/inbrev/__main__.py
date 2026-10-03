"""inbrev CLI: triage, eval, serve."""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from .config import settings


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="inbrev")
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("triage", help="triage messages from a JSONL file")
    t.add_argument("input", type=Path)
    t.add_argument("--out", type=Path, required=True)
    t.add_argument("--model", default=None)
    t.add_argument("--samples", type=int, default=None)
    t.add_argument("--temperature", type=float, default=None)
    t.add_argument("--no-schema", action="store_true")
    t.add_argument("--thinking", action="store_true")
    t.add_argument("--mode", choices=["admin", "clinical-triage"], default=None, help="admin (default) or clinical-triage (optional research mode, not a medical device)")
    t.add_argument("--limit", type=int, default=None)
    t.add_argument("--ids", nargs="*", default=None)

    e = sub.add_parser("eval", help="score prediction files against gold labels")
    e.add_argument("gold", type=Path)
    e.add_argument("predictions", type=Path, nargs="*")
    e.add_argument("--report", type=Path, default=None)
    e.add_argument("--baselines", action="store_true")

    r = sub.add_parser(
        "replay", help="re-run the deterministic checks on stored raw model output"
    )
    r.add_argument("messages", type=Path)
    r.add_argument("predictions", type=Path)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--safety-mode", default=None, choices=["llm", "lexical", "or"])
    r.add_argument("--mode", choices=["admin", "clinical-triage"], default=None, help="admin (default) or clinical-triage (optional research mode, not a medical device)")
    r.add_argument("--abstain-below", type=float, default=None)

    s = sub.add_parser("serve", help="start the web app")
    s.add_argument("--host", default="0.0.0.0")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--mode", choices=["admin", "clinical-triage"], default=None, help="admin (default) or clinical-triage (optional research mode, not a medical device)")

    args = p.parse_args(argv)
    cfg = settings()

    if args.cmd == "triage":
        from .pipeline import Options
        from .prompt import PROMPT_VERSION
        from .runner import read_jsonl, run_batch

        opts = Options.from_env(cfg)
        if args.mode:
            opts.mode = args.mode
        if args.samples is not None:
            opts.samples = args.samples
        if args.temperature is not None:
            opts.temperature = args.temperature
        opts.use_schema = not args.no_schema
        opts.thinking = args.thinking
        msgs = read_jsonl(args.input)
        if args.ids:
            msgs = [m for m in msgs if m["message_id"] in set(args.ids)]
        if args.limit:
            msgs = msgs[: args.limit]
        meta = {
            "model": args.model or cfg.llm_name,
            "samples": opts.samples,
            "temperature": opts.temperature,
            "schema": opts.use_schema,
            "thinking": opts.thinking,
            "prompt_version": PROMPT_VERSION,
            "safety_mode": opts.safety_mode,
            "abstain_below": opts.abstain_below,
            "started_at": datetime.now().isoformat(timespec="seconds"),
        }
        rows = asyncio.run(
            run_batch(msgs, args.out, cfg, opts, model=args.model, run_meta=meta)
        )
        errors = sum(1 for r in rows if r["trace"].get("error"))
        print(
            json.dumps({"written": len(rows), "errors": errors, "out": str(args.out)})
        )
    elif args.cmd == "replay":
        from .pipeline import Options, replay
        from .runner import read_jsonl

        opts = Options.from_env(cfg)
        if args.mode:
            opts.mode = args.mode
        if args.safety_mode:
            opts.safety_mode = args.safety_mode
        if args.abstain_below is not None:
            opts.abstain_below = args.abstain_below
        msgs = {m["message_id"]: m for m in read_jsonl(args.messages)}
        rows = [
            replay(row, msgs[row["result"]["message_id"]], opts)
            for row in read_jsonl(args.predictions)
        ]
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )
        print(json.dumps({"replayed": len(rows), "out": str(args.out)}))
    elif args.cmd == "eval":
        from .evaluate import main_eval

        main_eval(args.gold, args.predictions, args.report, args.baselines)
    elif args.cmd == "serve":
        import os
        import uvicorn

        if args.mode:
            os.environ["INBREV_MODE"] = args.mode

        uvicorn.run("inbrev.web:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
