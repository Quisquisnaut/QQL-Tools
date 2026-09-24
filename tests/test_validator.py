from __future__ import annotations

import json
import zipfile
from pathlib import Path

from qql_tools.qql.validator import validate_course_json_bytes, validate_path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "qql"


def _write_minimal_package(
    archive: zipfile.ZipFile,
    course_bytes: bytes,
    *,
    prefix: str = "",
) -> None:
    archive.writestr(
        f"{prefix}qql-course-package.json",
        json.dumps({"packageFormat": 1}),
    )
    archive.writestr(f"{prefix}course.json", course_bytes)


def test_package_importability() -> None:
    __import__("qql_tools")


def test_known_valid_minimal_qql_fixture(tmp_path: Path) -> None:
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    package_path = tmp_path / "minimal_valid_package.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        _write_minimal_package(archive, course_bytes)

    report = validate_path(package_path)

    assert report.is_valid is True
    assert report.is_fully_valid is False
    assert report.errors == []
    assert report.unsupported_checks


def test_malformed_json_reported() -> None:
    report = validate_course_json_bytes(
        (FIXTURES / "malformed.json").read_bytes(),
        source="malformed.json",
    )

    assert report.is_valid is False
    assert report.errors[0].code == "invalid-json"


def test_unsupported_model_version_reported() -> None:
    report = validate_course_json_bytes(
        (FIXTURES / "invalid_course_model_version.json").read_bytes()
    )

    assert any(error.code == "unsupported-format-version" for error in report.errors)


def test_malformed_package_structure_reported(tmp_path: Path) -> None:
    package_path = tmp_path / "bad.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        archive.writestr("course.json", "{}")

    report = validate_path(package_path)

    assert report.is_valid is False
    assert report.errors[0].code == "invalid-package"


def test_unsupported_package_version_reported(tmp_path: Path) -> None:
    package_path = tmp_path / "bad-format.zip"
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    with zipfile.ZipFile(package_path, "w") as archive:
        archive.writestr("qql-course-package.json", json.dumps({"packageFormat": 2}))
        archive.writestr("course.json", course_bytes)

    report = validate_path(package_path)

    assert report.is_valid is False
    assert report.errors[0].code == "invalid-package"
    assert "Unsupported package format" in report.errors[0].message


def test_flat_package_with_explicit_media_directory_entry_is_valid(tmp_path: Path) -> None:
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    package_path = tmp_path / "flat-media-dir.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        _write_minimal_package(archive, course_bytes)
        archive.writestr("media/", "")

    report = validate_path(package_path)

    assert report.is_valid is True
    assert report.errors == []


def test_wrapped_package_with_explicit_directory_entries_is_valid(tmp_path: Path) -> None:
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    package_path = tmp_path / "wrapped.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        archive.writestr("wrapped/", "")
        _write_minimal_package(archive, course_bytes, prefix="wrapped/")
        archive.writestr("wrapped/media/", "")

    report = validate_path(package_path)

    assert report.is_valid is True
    assert report.errors == []
    assert (
        "Accepted a single enclosing folder matching the ZIP filename stem."
        in report.notes
    )


def test_wrapped_package_with_unexpected_directory_rejected(tmp_path: Path) -> None:
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    package_path = tmp_path / "wrapped.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        archive.writestr("wrapped/", "")
        _write_minimal_package(archive, course_bytes, prefix="wrapped/")
        archive.writestr("wrapped/extra/", "")

    report = validate_path(package_path)

    assert report.is_valid is False
    assert report.errors[0].code == "invalid-package"
    assert "Unexpected archive entry: extra/" in report.errors[0].message


def test_unsafe_archive_path_handling(tmp_path: Path) -> None:
    package_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        archive.writestr("../course.json", "{}")
        archive.writestr(
            "../qql-course-package.json",
            json.dumps({"packageFormat": 1}),
        )

    report = validate_path(package_path)

    assert report.is_valid is False
    assert report.errors[0].code == "invalid-package"
    assert "Unsafe archive path" in report.errors[0].message


def test_unsafe_archive_directory_path_handling(tmp_path: Path) -> None:
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    package_path = tmp_path / "wrapped.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        archive.writestr("wrapped/", "")
        _write_minimal_package(archive, course_bytes, prefix="wrapped/")
        archive.writestr("wrapped/../", "")

    report = validate_path(package_path)

    assert report.is_valid is False
    assert report.errors[0].code == "invalid-package"
    assert "Unsafe archive path: ../" in report.errors[0].message


def test_unexpected_archive_file_rejection_unchanged(tmp_path: Path) -> None:
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    package_path = tmp_path / "unexpected-file.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        _write_minimal_package(archive, course_bytes)
        archive.writestr("unexpected.txt", "nope")

    report = validate_path(package_path)

    assert report.is_valid is False
    assert report.errors[0].code == "invalid-package"
    assert "Unexpected archive entry: unexpected.txt" in report.errors[0].message


def test_validator_reporting_shape() -> None:
    report = validate_course_json_bytes(
        (FIXTURES / "minimal_valid_course.json").read_bytes()
    )
    payload = report.to_dict()

    assert payload["is_valid"] is True
    assert payload["is_fully_valid"] is False
    assert "unsupported_checks" in payload
    assert payload["errors"] == []
