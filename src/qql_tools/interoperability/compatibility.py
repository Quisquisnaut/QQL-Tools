from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CompatibilityResult(StrEnum):
    EXACT = "Exact"
    MAPPED = "Mapped"
    APPROXIMATED = "Approximated"
    PRESERVED_BUT_UNUSED = "Preserved but unused"
    UNSUPPORTED = "Unsupported"
    REJECTED = "Rejected"


@dataclass(frozen=True)
class CompatibilityAssessment:
    feature: str
    qql_capability: str
    result: CompatibilityResult
    loss: str | None = None
    notes: str | None = None
