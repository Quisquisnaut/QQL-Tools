# QQL-Tools

Tools and converters for QQL and other language course formats.

## Purpose

QQL-Tools is an independent companion project to QuisquisLingo (QQL).

This repository focuses on format tooling, including:

- converting external course formats into QQL;
- potentially converting QQL courses to other formats;
- validating QQL Course files and packages;
- inspecting Course structures;
- producing conversion and compatibility reports;
- supporting future migration and format utilities.

## Scope boundary

QQL-Tools is not a copy of the QuisquisLingo Flutter application.

- Keep Flutter UI and application-specific runtime services out of this repository.
- Reuse QQL code only when it is truly reusable parsing, format, validation, or interoperability logic.

## QQL reference source

QuisquisLingo is the authoritative reference for QQL structure and behavior.

When implementing tools in this repository, verify against the current QuisquisLingo `main` branch for:

- Course Model and package format;
- JSON structure and hierarchy;
- IDs and references;
- exercise primitives and presets;
- media representation;
- validation and metadata rules.

## Planned conversion pipeline

```text
External course format
→ format-specific parser
→ normalized course representation
→ compatibility analysis
→ QQL mapping
→ QQL Course package
→ independent QQL validation
```

## Technology

- Python 3
- `pyproject.toml`-based project
- `pytest` for tests
- standard library first by default

## CLI direction

Initial command layout:

```text
qql-tools validate <file>
qql-tools inspect <file>
qql-tools convert --from <format> <file>
```

## License

This project is licensed under Mozilla Public License 2.0 (MPL-2.0).
See [`LICENSE`](./LICENSE).
