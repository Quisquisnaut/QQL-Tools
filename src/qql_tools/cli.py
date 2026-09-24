"""CLI entrypoint for QQL-Tools."""

from __future__ import annotations

import argparse
from collections.abc import Sequence


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qql-tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a QQL Course file or package")
    validate.add_argument("file", help="Path to file or package to validate")

    inspect = subparsers.add_parser("inspect", help="Inspect a QQL Course file or package")
    inspect.add_argument("file", help="Path to file or package to inspect")

    convert = subparsers.add_parser("convert", help="Convert a source format into QQL")
    convert.add_argument("--from", dest="source_format", required=True, help="Source format identifier")
    convert.add_argument("file", help="Path to source course file")

    return parser


def _not_implemented(command_name: str) -> int:
    print(f"{command_name} is not implemented yet")
    return 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate":
        return _not_implemented("validate")
    if args.command == "inspect":
        return _not_implemented("inspect")
    if args.command == "convert":
        return _not_implemented("convert")

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
