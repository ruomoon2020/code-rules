#!/usr/bin/env python3
"""Generate evals/topic-manifest.yaml for a rules package.

Usage:
  python scripts/generate-eval-topic-manifest.py --rules-dir web-front/rules
  python scripts/generate-eval-topic-manifest.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from eval_topic_manifest import build_manifest, write_manifest  # noqa: E402

PACKAGES = [
    ("web-front/rules", "E"),
    ("web-backend/rules", "B"),
    ("miniapp/rules", "M"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules-dir", type=Path, help="Path to rules/ package root")
    parser.add_argument(
        "--id-prefix",
        choices=["E", "B", "M"],
        help="Eval ID prefix (default: infer from package)",
    )
    parser.add_argument("--all", action="store_true", help="Regenerate all three packages")
    args = parser.parse_args()

    targets: list[tuple[Path, str]] = []
    if args.all:
        for rel, prefix in PACKAGES:
            targets.append((ROOT / rel, prefix))
    elif args.rules_dir:
        rules = args.rules_dir if args.rules_dir.is_absolute() else ROOT / args.rules_dir
        prefix = args.id_prefix
        if not prefix:
            if "web-front" in rules.parts:
                prefix = "E"
            elif "web-backend" in rules.parts:
                prefix = "B"
            elif "miniapp" in rules.parts:
                prefix = "M"
            else:
                print("Cannot infer id-prefix; pass --id-prefix", file=sys.stderr)
                return 1
        targets.append((rules, prefix))
    else:
        parser.print_help()
        return 1

    for rules_root, prefix in targets:
        out = write_manifest(rules_root, prefix)
        entry_count = len(build_manifest(rules_root, prefix).get("entries", {}))
        print(f"Wrote {out} ({prefix}, {entry_count} entries)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
