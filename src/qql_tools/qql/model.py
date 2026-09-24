from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .versions import QQL_COURSE_MODEL_VERSION


@dataclass(frozen=True)
class CourseEnvelope:
    data: dict[str, Any]

    @property
    def format_version(self) -> int | None:
        value = self.data.get("formatVersion")
        return value if isinstance(value, int) else None

    @property
    def course_id(self) -> str | None:
        value = self.data.get("courseId")
        return value if isinstance(value, str) and value.strip() else None

    @property
    def lessons(self) -> list[dict[str, Any]] | None:
        value = self.data.get("lessons")
        if not isinstance(value, list):
            return None
        return [item for item in value if isinstance(item, dict)]

    def is_supported_version(self) -> bool:
        return self.format_version == QQL_COURSE_MODEL_VERSION
