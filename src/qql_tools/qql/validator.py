from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .model import CourseEnvelope
from .package import parse_package
from .versions import COURSE_JSON_NAME, PACKAGE_MANIFEST_NAME, QQL_COURSE_MODEL_VERSION

_SUPPORTED_PUBLICATION_STATES = {"draft", "published"}
_SUPPORTED_LESSON_NUMBERING_MODES = {
    "lesson",
    "unit",
    "topic",
    "module",
    "skill",
    "chapter",
    "stage",
    "step",
    "part",
    "other",
    "numberOnly",
    "none",
}
_SUPPORTED_LESSON_ICON_STYLES = {"monochrome", "coloredLessonNumbers"}
_SUPPORTED_ROUND_VISUAL_TYPES = {"listening", "story", "generic", "test"}
_UTC_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")

SUPPORTED_VALIDATION_SCOPE = (
    "JSON decoding",
    "QQL course model version",
    "QQL package format version",
    "required package members",
    "archive path safety",
    "required top-level course fields",
    "basic lesson / round structural fields",
)
UNSUPPORTED_VALIDATION_SCOPE = (
    "full lesson/round/exercise schema validation",
    "cross-reference integrity",
    "media digest verification",
    "shared image manifest verification",
    "publisher signature / checksum verification",
)


@dataclass
class ValidationMessage:
    code: str
    message: str
    location: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {"code": self.code, "message": self.message}
        if self.location is not None:
            data["location"] = self.location
        return data


@dataclass
class ValidationReport:
    source: str
    implemented_checks: tuple[str, ...] = SUPPORTED_VALIDATION_SCOPE
    unsupported_checks: list[str] = field(
        default_factory=lambda: list(UNSUPPORTED_VALIDATION_SCOPE)
    )
    errors: list[ValidationMessage] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    @property
    def is_fully_valid(self) -> bool:
        return self.is_valid and not self.unsupported_checks

    def add_error(self, code: str, message: str, location: str | None = None) -> None:
        self.errors.append(ValidationMessage(code=code, message=message, location=location))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "implemented_checks": list(self.implemented_checks),
            "unsupported_checks": list(self.unsupported_checks),
            "errors": [error.to_dict() for error in self.errors],
            "is_valid": self.is_valid,
            "is_fully_valid": self.is_fully_valid,
            "notes": list(self.notes),
        }


def _decode_course_json(raw: bytes, source: str, report: ValidationReport) -> dict[str, Any] | None:
    try:
        decoded = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        report.add_error("invalid-encoding", str(exc), source)
        return None
    except json.JSONDecodeError as exc:
        report.add_error("invalid-json", exc.msg, f"{source}:{exc.lineno}:{exc.colno}")
        return None
    if not isinstance(decoded, dict):
        report.add_error("invalid-root", "Top-level course JSON must be an object.", source)
        return None
    return decoded


def _require_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_timestamp(value: Any, location: str, report: ValidationReport) -> None:
    if not _require_non_empty_string(value) or not _UTC_TIMESTAMP_RE.fullmatch(value):
        report.add_error(
            "invalid-timestamp",
            "Timestamp must be a UTC ISO-8601 string ending in 'Z'.",
            location,
        )


def _validate_course_dict(data: dict[str, Any], report: ValidationReport) -> None:
    course = CourseEnvelope(data)
    if course.format_version != QQL_COURSE_MODEL_VERSION:
        report.add_error(
            "unsupported-format-version",
            f"Supported QQL course model is {QQL_COURSE_MODEL_VERSION}; found {data.get('formatVersion')!r}.",
            "formatVersion",
        )
    if data.get("publicationState") not in _SUPPORTED_PUBLICATION_STATES:
        report.add_error(
            "invalid-publication-state",
            "publicationState must be 'draft' or 'published'.",
            "publicationState",
        )
    if data.get("lessonNumberingMode") not in _SUPPORTED_LESSON_NUMBERING_MODES:
        report.add_error(
            "invalid-lesson-numbering-mode",
            "lessonNumberingMode is missing or invalid for QQL Course Model v11.",
            "lessonNumberingMode",
        )
    if data.get("defaultLessonIconStyle") not in _SUPPORTED_LESSON_ICON_STYLES:
        report.add_error(
            "invalid-default-lesson-icon-style",
            "defaultLessonIconStyle is missing or invalid for QQL Course Model v11.",
            "defaultLessonIconStyle",
        )
    if course.course_id is None:
        report.add_error("missing-course-id", "courseId must be a non-empty string.", "courseId")

    lessons = data.get("lessons")
    if not isinstance(lessons, list):
        report.add_error("missing-lessons", "lessons must be an array.", "lessons")
        return
    for index, lesson in enumerate(lessons):
        location = f"lessons[{index}]"
        if not isinstance(lesson, dict):
            report.add_error("invalid-lesson", "Each lesson must be an object.", location)
            continue
        for key in ("lessonId", "title"):
            if not _require_non_empty_string(lesson.get(key)):
                report.add_error(
                    "missing-lesson-field",
                    f"Lesson is missing required field {key}.",
                    f"{location}.{key}",
                )
        if lesson.get("publicationState") not in _SUPPORTED_PUBLICATION_STATES:
            report.add_error(
                "invalid-lesson-publication-state",
                "Lesson publicationState must be 'draft' or 'published'.",
                f"{location}.publicationState",
            )
        _validate_timestamp(lesson.get("updatedAt"), f"{location}.updatedAt", report)
        if not isinstance(lesson.get("guidebook"), dict):
            report.add_error(
                "missing-guidebook",
                "Lesson guidebook must be present as an object.",
                f"{location}.guidebook",
            )
        if not isinstance(lesson.get("duel"), dict):
            report.add_error(
                "missing-duel",
                "Lesson duel must be present as an object.",
                f"{location}.duel",
            )
        rounds = lesson.get("rounds")
        if not isinstance(rounds, list):
            report.add_error("missing-rounds", "Lesson rounds must be an array.", f"{location}.rounds")
            continue
        for round_index, round_obj in enumerate(rounds):
            round_location = f"{location}.rounds[{round_index}]"
            if not isinstance(round_obj, dict):
                report.add_error("invalid-round", "Each round must be an object.", round_location)
                continue
            for key in ("id",):
                if not _require_non_empty_string(round_obj.get(key)):
                    report.add_error(
                        "missing-round-field",
                        f"Round is missing required field {key}.",
                        f"{round_location}.{key}",
                    )
            if round_obj.get("publicationState") not in _SUPPORTED_PUBLICATION_STATES:
                report.add_error(
                    "invalid-round-publication-state",
                    "Round publicationState must be 'draft' or 'published'.",
                    f"{round_location}.publicationState",
                )
            _validate_timestamp(round_obj.get("updatedAt"), f"{round_location}.updatedAt", report)
            if round_obj.get("visualType") not in _SUPPORTED_ROUND_VISUAL_TYPES:
                report.add_error(
                    "invalid-round-visual-type",
                    "Round visualType is missing or invalid.",
                    f"{round_location}.visualType",
                )
            content = round_obj.get("content")
            if not isinstance(content, list):
                report.add_error(
                    "missing-content",
                    "Round content must be an array.",
                    f"{round_location}.content",
                )


def validate_course_json_bytes(raw: bytes, source: str = COURSE_JSON_NAME) -> ValidationReport:
    report = ValidationReport(source=source)
    data = _decode_course_json(raw, source, report)
    if data is not None:
        _validate_course_dict(data, report)
    return report


def validate_path(path: Path) -> ValidationReport:
    path = path.resolve()
    if path.suffix.lower() == ".zip":
        report = ValidationReport(source=str(path))
        try:
            package = parse_package(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            report.add_error("invalid-package", str(exc), str(path))
            return report
        nested_report = validate_course_json_bytes(
            package.course_json,
            source=f"{path.name}:{COURSE_JSON_NAME}",
        )
        report.errors.extend(nested_report.errors)
        report.unsupported_checks = list(
            dict.fromkeys(report.unsupported_checks + nested_report.unsupported_checks)
        )
        report.notes.append(
            f"Parsed package manifest {PACKAGE_MANIFEST_NAME} (format {package.manifest.get('packageFormat')})"
        )
        if package.had_matching_folder_wrapper:
            report.notes.append(
                "Accepted a single enclosing folder matching the ZIP filename stem."
            )
        return report
    return validate_course_json_bytes(path.read_bytes(), source=str(path))
