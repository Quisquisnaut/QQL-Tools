from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):
    SINGLE_SELECTION = "single_selection"
    MULTIPLE_SELECTION = "multiple_selection"
    TEXT_INPUT = "text_input"
    ORDERING = "ordering"
    MATCHING = "matching"
    PRESENTATION = "presentation"
    INLINE_GAPS = "inline_gaps"
    MULTIPLE_GAPS = "multiple_gaps"
    IMAGE = "image"
    AUDIO = "audio"
    LANGUAGE_DIRECTION = "language_direction"
    IMMEDIATE_EVALUATION = "immediate_evaluation"
    EXPLICIT_SUBMIT = "explicit_submit"
