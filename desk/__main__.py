"""python -m desk <command>

  generate --stats            what the generator produces (15,000 incidents + the live 12-hour window), without storing it
  build-rag [--explain] [--bench]   load -> clean -> chunk -> embed -> index -> verify, every collection (idempotent)
  profile                     bucket the 15,000 incidents, measured against the held-out answer key
  retrieval-eval              per-source retrieval metrics, prefix ablation, merged-vs-split, Agno's built-in hybrid vs ours
  tools-smoke                 call every tool once against the mocks
  ask --user u-priya "..."    one question through the Agno workflow
  eval [--scenarios]          the labelled scenarios: route, sources, tools, citations
  knowledge-fix --demo        gap cluster -> draft -> approve -> re-index -> re-run the gap questions
  ingest                      what the ingest container runs: build-rag + profile + gates (skips work already done)
  health                      every service's health
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings

warnings.filterwarnings("ignore")
import logging  # noqa: E402

logging.getLogger("agno").setLevel(logging.WARNING)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="desk")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate"); g.add_argument("--stats", action="store_true")
    b = sub.add_parser("build-rag"); b.add_argument("--explain", action="store_true"); b.add_argument("--bench", action="store_true")
    sub.add_parser("profile")
    sub.add_parser("retrieval-eval")
    sub.add_parser("tools-smoke")
    a = sub.add_parser("ask"); a.add_argument("--user", default="u-priya"); a.add_argument("message"); a.add_argument("--confirm", action="store_true")
    e = sub.add_parser("eval"); e.add_argument("--scenarios", action="store_true"); e.add_argument("--only")
    k = sub.add_parser("knowledge-fix"); k.add_argument("--demo", action="store_true")
    sub.add_parser("ingest")
    sub.add_parser("health")
    args = ap.parse_args(argv)

    if args.cmd == "generate":
        from desk.generate import generate, stats
        h, key, live = generate()
        print(stats(h, key, live))
    elif args.cmd == "build-rag":
        from desk.rag.build import build
        build(explain=True, bench=args.bench)
    elif args.cmd == "profile":
        from desk.profile import run
        run(explain=True)
    elif args.cmd == "retrieval-eval":
        from desk.retrieval_eval import run
        run()
    elif args.cmd == "tools-smoke":
        from desk.smoke import tools_smoke
        tools_smoke()
    elif args.cmd == "ask":
        from desk.workflow import ask, confirm
        r = ask(args.user, args.message)
        print(json.dumps(r, indent=1))
        if args.confirm and r.get("pending"):
            print(json.dumps(confirm(r["pending"]), indent=1))
    elif args.cmd == "eval":
        from desk.evaluate import run
        run(only=args.only)
    elif args.cmd == "knowledge-fix":
        from desk.knowledge_fix import demo
        demo()
    elif args.cmd == "ingest":
        from desk.ingest import run
        run()
    elif args.cmd == "health":
        from desk.smoke import health
        print(json.dumps(health(), indent=1))


if __name__ == "__main__":
    main()
