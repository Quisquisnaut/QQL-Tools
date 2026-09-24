from __future__ import annotations

QQL_COURSE_MODEL_VERSION = 11
QQL_PACKAGE_FORMAT_VERSION = 1
QQL_CANONICAL_EXERCISE_MODELS = (
    "select",
    "input",
    "arrange",
    "match",
    "presentation",
)

MEDIA_REFERENCE_PREFIX = "media:"
SUPPORTED_MEDIA_EXTENSIONS = frozenset({"mp3", "png", "jpg", "jpeg", "webp"})
SUPPORTED_IMAGE_EXTENSIONS = frozenset({"png", "jpg", "jpeg", "webp"})
SUPPORTED_AUDIO_EXTENSIONS = frozenset({"mp3"})
PACKAGE_MANIFEST_NAME = "qql-course-package.json"
COURSE_JSON_NAME = "course.json"
