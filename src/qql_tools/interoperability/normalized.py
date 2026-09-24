from __future__ import annotations

from dataclasses import dataclass, field

from .capabilities import Capability


@dataclass(frozen=True)
class NormalizedExercise:
    primitive: str
    capabilities: frozenset[Capability] = field(default_factory=frozenset)
    prompt: str | None = None


@dataclass(frozen=True)
class NormalizedRound:
    title: str
    exercises: tuple[NormalizedExercise, ...] = ()


@dataclass(frozen=True)
class NormalizedLesson:
    title: str
    rounds: tuple[NormalizedRound, ...] = ()


@dataclass(frozen=True)
class NormalizedCourse:
    title: str
    source_language: str | None = None
    target_language: str | None = None
    lessons: tuple[NormalizedLesson, ...] = ()
