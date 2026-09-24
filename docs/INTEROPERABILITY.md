# Interoperability boundary

QQL-Tools is intended to keep external conversion logic separate from any one UI implementation and separate from any one external source platform.

## Intended pipeline

```text
External format
→ parser
→ normalized representation
→ capability analysis
→ target QQL mapper
→ QQL package writer
→ QQL validator
```

## Canonical QQL exercise layer

The current canonical QQL exercise primitives verified from QuisquisLingo are:

- Select
- Input
- Arrange
- Match
- Presentation

These primitives are a more stable semantic target than current editor-facing preset names. A future converter should normally reason in terms of:

```text
external semantics
→ normalized semantics/capabilities
→ QQL primitive
→ target-version-specific QQL preset/configuration
```

not by directly hard-coding an external type to today's preset list.

## Normalized representation

The normalized layer in this repository is intentionally small in the first milestone. It captures:

- course-level identity and language metadata;
- lesson / round structure;
- normalized exercises with semantic primitive plus capabilities;
- enough compatibility metadata to describe mapping quality and information loss.

It is deliberately **not** a full universal course schema, and it is deliberately **not** coupled to QQL Course Model v11 field-for-field.

## Version boundary

External parsers should target the normalized representation, not a specific QQL model version. QQL-specific serialization belongs in the mapper/package layer so a future QQL v12 mapper can be added without rewriting external parsers.
