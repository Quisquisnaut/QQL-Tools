from __future__ import annotations

import json
import zipfile
from pathlib import Path

from qql_tools.cli import main
from qql_tools.qql import validator as validator_module
from qql_tools.qql.validator import validate_path

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "qql"


def _write_package(
    package_path: Path,
    course_bytes: bytes,
    *,
    package_format: int = 1,
    wrapper: bool = False,
) -> None:
    with zipfile.ZipFile(package_path, "w") as archive:
        prefix = f"{package_path.stem}/" if wrapper else ""
        archive.writestr(
            f"{prefix}qql-course-package.json",
            json.dumps({"packageFormat": package_format}),
        )
        archive.writestr(f"{prefix}course.json", course_bytes)


def test_validate_cli_human_readable_partial_output_for_package(
    tmp_path: Path, capsys
) -> None:
    package_path = tmp_path / "minimal_valid_package.zip"
    _write_package(
        package_path,
        (FIXTURES / "minimal_valid_course.json").read_bytes(),
        wrapper=True,
    )

    exit_code = main(["validate", str(package_path)])

    assert exit_code == 2
    output = capsys.readouterr().out
    assert f"Path: {package_path.resolve()}" in output
    assert "Input: QQL package ZIP" in output
    assert "Detected Course Model version: 11" in output
    assert "Detected package format: 1" in output
    assert "Result: VALID for all currently implemented checks" in output
    assert "Checks performed:" in output
    assert "Checks not yet implemented:" in output
    assert "Accepted a single enclosing folder matching the ZIP filename stem." in output


def test_validate_cli_human_readable_full_valid_output(capsys, monkeypatch) -> None:
    course_path = FIXTURES / "minimal_valid_course.json"
    monkeypatch.setattr(validator_module, "UNSUPPORTED_VALIDATION_SCOPE", ())

    exit_code = main(["validate", str(course_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert f"Path: {course_path.resolve()}" in output
    assert "Input: JSON Course" in output
    assert "Detected Course Model version: 11" in output
    assert "Result: FULLY VALID" in output
    assert "Checks not yet implemented:" not in output


def test_validate_cli_human_readable_invalid_output(capsys) -> None:
    course_path = FIXTURES / "invalid_course_model_version.json"

    exit_code = main(["validate", str(course_path)])

    assert exit_code == 1
    output = capsys.readouterr().out
    lines = output.splitlines()
    assert lines[0] == "Result: INVALID"
    assert f"Path: {course_path.resolve()}" in output
    assert "Input: JSON Course" in output
    assert "Detected Course Model version: 99" in output
    assert "Errors:" in output
    assert "- formatVersion: Supported QQL course model is 11; found 99." in output
    assert output.index("Errors:") < output.index("Checks performed:")


def test_validate_cli_json_output_and_exit_code(tmp_path: Path, capsys) -> None:
    package_path = tmp_path / "minimal_valid_package.zip"
    _write_package(
        package_path,
        (FIXTURES / "minimal_valid_course.json").read_bytes(),
    )

    exit_code = main(["validate", str(package_path), "--json"])

    assert exit_code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload == validate_path(package_path).to_dict()
    assert "Detected package format" not in json.dumps(payload)
