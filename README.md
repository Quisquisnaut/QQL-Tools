# QQL-Tools

Tools and converters for QQL and other language course formats.

QQL-Tools is a separate companion repository to [QuisquisLingo](https://github.com/Quisquisnaut/QuisquisLingo). It exists to document, inspect, validate, and eventually convert course packages without turning this repository into another copy of the Flutter application.

## Scope

The intended long-term pipeline is:

```text
External course format
→ format-specific parser
→ normalized representation
→ compatibility analysis
→ QQL mapping
→ QQL Course package
→ independent QQL validation
```

This repository currently provides:

- documentation of the current QQL interchange contract as verified against QuisquisLingo `main`;
- a small Python package with QQL version constants, package helpers, compatibility result types, and a conservative validator foundation;
- fixture-driven tests for the implemented validation behavior.

This repository does **not** yet provide:

- any external-platform converter;
- full QQL schema validation;
- a GUI or Flutter application;
- speculative support for future QQL model versions.

## Relationship to QuisquisLingo

QuisquisLingo remains the authoritative implementation for the current QQL course model and package format. QQL-Tools is intentionally independent at runtime and does not import or invoke QuisquisLingo.

The current canonical QQL exercise primitives verified from QuisquisLingo are:

- Select
- Input
- Arrange
- Match
- Presentation

Those primitives are treated here as a more stable semantic layer than editor-facing preset names, which remain free to evolve.

## Development

Create a virtual environment and install test dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Run the current CLI help:

```bash
python -m qql_tools.cli --help
```

Try the conservative validator:

```bash
python -m qql_tools.cli validate fixtures/qql/minimal_valid_course.json
```

The current validator returns a non-zero exit code when unsupported checks remain, so it does not silently claim complete validity while the independent rule set is still incomplete.

## License

QQL-Tools is licensed under the Mozilla Public License 2.0 (MPL-2.0), matching QuisquisLingo so reusable format and validation logic can move between the repositories without unnecessary relicensing friction.
