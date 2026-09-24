from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .versions import (
    COURSE_JSON_NAME,
    PACKAGE_MANIFEST_NAME,
    QQL_PACKAGE_FORMAT_VERSION,
)

_MEDIA_ENTRY_RE = re.compile(r"^media/[0-9a-f]{64}\.(mp3|png|jpg|jpeg|webp)$")


@dataclass(frozen=True)
class PackageContents:
    manifest: dict[str, Any]
    course_json: bytes
    media_entries: tuple[str, ...]
    had_matching_folder_wrapper: bool


def _matching_wrapper_prefix(names: list[str], archive_name: str | None) -> str | None:
    if not archive_name or not archive_name.lower().endswith(".zip"):
        return None
    stem = Path(archive_name).name[:-4]
    if not stem or any(ch in stem for ch in ("/", "\\")):
        return None
    prefix = f"{stem}/"
    return prefix if names and all(name.startswith(prefix) for name in names) else None


def _normalize_zip_names(names: list[str], archive_name: str | None) -> tuple[list[str], bool]:
    prefix = _matching_wrapper_prefix(names, archive_name)
    if prefix is None:
        return names, False
    return [name[len(prefix) :] for name in names], True


def _is_safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        not path.is_absolute()
        and ".." not in path.parts
        and not any(part in {"", "."} for part in path.parts)
    )


def parse_package(path: Path) -> PackageContents:
    with zipfile.ZipFile(path) as archive:
        original_names = archive.namelist()
        normalized_names, had_wrapper = _normalize_zip_names(original_names, path.name)
        name_map = dict(zip(normalized_names, original_names, strict=True))
        for normalized_name in normalized_names:
            if not _is_safe_name(normalized_name):
                raise ValueError(f"Unsafe archive path: {normalized_name}")
            if normalized_name in {PACKAGE_MANIFEST_NAME, COURSE_JSON_NAME}:
                continue
            if _MEDIA_ENTRY_RE.fullmatch(normalized_name):
                continue
            raise ValueError(f"Unexpected archive entry: {normalized_name}")
        if PACKAGE_MANIFEST_NAME not in name_map or COURSE_JSON_NAME not in name_map:
            raise ValueError("Missing package manifest or course.json")
        manifest = json.loads(archive.read(name_map[PACKAGE_MANIFEST_NAME]).decode("utf-8"))
        if not isinstance(manifest, dict) or manifest.get("packageFormat") != QQL_PACKAGE_FORMAT_VERSION:
            raise ValueError("Unsupported package format")
        if any(key not in {"packageFormat", "sharedImageSources"} for key in manifest):
            raise ValueError("Unsupported package manifest keys")
        course_json = archive.read(name_map[COURSE_JSON_NAME])
        media_entries = tuple(sorted(name for name in normalized_names if name.startswith("media/")))
        return PackageContents(
            manifest=manifest,
            course_json=course_json,
            media_entries=media_entries,
            had_matching_folder_wrapper=had_wrapper,
        )
