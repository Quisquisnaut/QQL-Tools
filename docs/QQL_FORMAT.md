# QQL format foundation

This document summarizes the **current external interchange contract** that independent tools need, as verified against `Quisquisnaut/QuisquisLingo` `main`. It intentionally distinguishes serialized format requirements from application-internal implementation details.

## Verified current versions

- **QQL Course Model:** v11 (`formatVersion: 11`)
- **QQL Course package format:** 1 (`qql-course-package.json`)

These values are treated here as the current source of truth, but QQL-Tools is structured so future mappers and validators can add later QQL versions without rewriting external parsers.

## Stable serialized contract

### Course JSON

A native current-format course is serialized as `course.json`. QuisquisLingo's current documentation and model implementation establish these current root requirements:

- `formatVersion: 11`
- `publicationState: "draft" | "published"`
- `lessonNumberingMode`
- `defaultLessonIconStyle`
- `courseId` as immutable course identity
- `lessons` as the ordered lesson list

QuisquisLingo currently documents the hierarchy as:

```text
Course > lessons[] > guidebook + rounds[] + duel > content[]
```

Current lesson and round objects also carry stable IDs, publication state, and UTC `updatedAt` timestamps. This first milestone documents and validates only the parts of that structure that are confidently verified and useful to independent tooling.

### Package structure

Portable QQL packages are ZIP archives containing:

- `qql-course-package.json`
- `course.json`
- `media/<sha256>.<ext>` for each referenced course-owned media file

Current package format is:

```json
{"packageFormat": 1}
```

QuisquisLingo also accepts a single enclosing ZIP folder when its name exactly matches the ZIP file stem. Other unexpected or unsafe layouts are rejected.

### Media references

Current QQL course-owned media references use the form:

```text
media:<sha256>.<ext>
```

QuisquisLingo's currently documented/implemented portable extensions are:

- audio: `mp3`
- images: `png`, `jpg`, `jpeg`, `webp`

Absolute or device-relative filesystem paths are not part of the portable contract.

## Canonical exercise primitives

QuisquisLingo currently defines five canonical exercise models:

- `select`
- `input`
- `arrange`
- `match`
- `presentation`

These are the stable interoperability target for QQL-Tools. Preset names such as specific translation, listening, or gap workflows are an authoring layer above these primitives and should not be treated as the long-term conversion contract.

## Metadata and provenance

QuisquisLingo v11 currently serializes richer metadata than older course formats, including concepts for:

- publication state;
- origin type and versioning;
- authorship and rights metadata;
- provenance and fork lineage;
- maintainer/editor snapshots;
- optional descriptive metadata such as keywords, cover image, and image library.

QQL-Tools does not yet attempt to fully normalize or validate all of those fields independently, but preserves them as important documented parts of the interchange contract.

## Validation expectations for independent tools

A safe independent validator should eventually check at least:

- JSON parseability;
- supported course model version;
- supported package format version;
- required package members;
- archive path safety;
- required top-level course structure;
- ID and reference integrity;
- exercise structure;
- media reference integrity;
- model/package compatibility.

In this first milestone, QQL-Tools implements only the subset of those checks that is already grounded in the verified upstream contract, and reports deeper checks explicitly as unsupported rather than silently claiming success.

## Current scope limit

This document intentionally excludes Flutter UI details, editor widgets, and unrelated application services unless they directly affect serialized interoperability.
