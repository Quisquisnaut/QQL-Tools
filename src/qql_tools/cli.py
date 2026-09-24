from __future__ import annotations

import argparse
import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .qql.package import COURSE_JSON_NAME, PACKAGE_MANIFEST_NAME
from .qql.validator import validate_path


@dataclass
class ValidationDisplayDetails:
    input_type: str | None = None
    course_model_version: Any | None = None
    package_format: Any | None = None
    notes: list[str] = field(default_factory=list)


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
    validate_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the structured JSON validation report.",
    )
    return parser


def _matching_wrapper_prefix(names: list[str], archive_name: str | None) -> str | None:
    if not archive_name or not archive_name.lower().endswith(".zip"):
        return None
    stem = Path(archive_name).name[:-4]
    if not stem or any(ch in stem for ch in ("/", "\\")):
        return None
    prefix = f"{stem}/"
    return prefix if names and all(name.startswith(prefix) for name in names) else None


def _normalize_zip_names(names: list[str], archive_name: str | None) -> tuple[list[str], bool]:
    prefix = _matching_wrapper_prefix(names, archive_name)
    if prefix is None:
        return names, False
    return [name[len(prefix) :] for name in names], True


def _detect_course_model_version(raw: bytes) -> Any | None:
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(decoded, dict):
        return None
    return decoded.get("formatVersion")


def _collect_display_details(path: Path) -> ValidationDisplayDetails:
    path = path.resolve()
    if path.suffix.lower() != ".zip":
        return ValidationDisplayDetails(
            input_type="JSON Course",
            course_model_version=_detect_course_model_version(path.read_bytes()),
        )

    details = ValidationDisplayDetails(input_type="QQL package ZIP")
    try:
        with zipfile.ZipFile(path) as archive:
            original_names = archive.namelist()
            normalized_names, had_wrapper = _normalize_zip_names(original_names, path.name)
            name_map = dict(zip(normalized_names, original_names, strict=True))
            if had_wrapper:
                details.notes.append(
                    "Accepted a single enclosing folder matching the ZIP filename stem."
                )
            manifest_name = name_map.get(PACKAGE_MANIFEST_NAME)
            if manifest_name is not None:
                try:
                    manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    manifest = None
                if isinstance(manifest, dict):
                    details.package_format = manifest.get("packageFormat")
            course_name = name_map.get(COURSE_JSON_NAME)
            if course_name is not None:
                details.course_model_version = _detect_course_model_version(
                    archive.read(course_name)
                )
    except (OSError, ValueError, zipfile.BadZipFile):
        pass
    return details


def _result_text(is_valid: bool, is_fully_valid: bool) -> str:
    if not is_valid:
        return "INVALID"
    if is_fully_valid:
        return "FULLY VALID"
    return "VALID for all currently implemented checks"


def _format_error(location: str | None, message: str) -> str:
    if location:
        return f"- {location}: {message}"
    return f"- {message}"


def format_validation_report(path: Path, report: Any) -> str:
    path = path.resolve()
    details = _collect_display_details(path)
    notes = list(dict.fromkeys([*report.notes, *details.notes]))
    metadata_lines = [f"Path: {path}"]
    if details.input_type is not None:
        metadata_lines.append(f"Input: {details.input_type}")
    if details.course_model_version is not None:
        metadata_lines.append(f"Detected Course Model version: {details.course_model_version}")
    if details.package_format is not None:
        metadata_lines.append(f"Detected package format: {details.package_format}")
    lines: list[str] = []

    if not report.is_valid:
        lines.append("Result: INVALID")
        lines.extend(metadata_lines)
        lines.append("")
        lines.append("Errors:")
        lines.extend(_format_error(error.location, error.message) for error in report.errors)
    else:
        lines.extend(metadata_lines)
        lines.append(f"Result: {_result_text(report.is_valid, report.is_fully_valid)}")

    if report.implemented_checks:
        lines.append("")
        lines.append("Checks performed:")
        lines.extend(f"- {check}" for check in report.implemented_checks)
    if report.unsupported_checks:
        lines.append("")
        lines.append("Checks not yet implemented:")
        lines.extend(f"- {check}" for check in report.unsupported_checks)
    if notes:
        lines.append("")
        lines.append("Notes:")
        lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines)


def _validation_exit_code(report: Any) -> int:
    if not report.is_valid:
        return 1
    if report.is_fully_valid:
        return 0
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "validate":
        report = validate_path(args.path)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        else:
            print(format_validation_report(args.path, report))
        return _validation_exit_code(report)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
