from __future__ import annotations

import argparse
import json
from pathlib import Path

from .qql.validator import validate_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qql-tools",
        description="Independent tools for QQL course formats.",
    )
    subparsers = parser.add_subparsers(dest="command")

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a QQL course JSON file or package ZIP using implemented QQL-Tools checks.",
    )
    validate_parser.add_argument("path", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "validate":
        report = validate_path(args.path)
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        return 0 if report.is_fully_valid else 2
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
