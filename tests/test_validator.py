from __future__ import annotations

import json
import zipfile
from pathlib import Path

from qql_tools.qql.validator import validate_course_json_bytes, validate_path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "qql"


def test_package_importability() -> None:
    __import__("qql_tools")


def test_known_valid_minimal_qql_fixture(tmp_path: Path) -> None:
    course_bytes = (FIXTURES / "minimal_valid_course.json").read_bytes()
    package_path = tmp_path / "minimal_valid_package.zip"
    with zipfile.ZipFile(package_path, "w") as archive:
        archive.writestr("qql-course-package.json", json.dumps({"packageFormat": 1}))
        archive.writestr("course.json", course_bytes)

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


def test_validator_reporting_shape() -> None:
    report = validate_course_json_bytes(
        (FIXTURES / "minimal_valid_course.json").read_bytes()
    )
    payload = report.to_dict()

    assert payload["is_valid"] is True
    assert payload["is_fully_valid"] is False
    assert "unsupported_checks" in payload
    assert payload["errors"] == []
