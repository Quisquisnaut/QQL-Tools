from qql_tools.cli import main


def test_validate_placeholder_returns_nonzero(capsys):
    code = main(["validate", "course.json"])
    out = capsys.readouterr().out
    assert code == 1
    assert "validate is not implemented yet" in out


def test_inspect_placeholder_returns_nonzero(capsys):
    code = main(["inspect", "course.json"])
    out = capsys.readouterr().out
    assert code == 1
    assert "inspect is not implemented yet" in out


def test_convert_placeholder_requires_source_format(capsys):
    code = main(["convert", "--from", "anki", "course.apkg"])
    out = capsys.readouterr().out
    assert code == 1
    assert "convert is not implemented yet" in out
