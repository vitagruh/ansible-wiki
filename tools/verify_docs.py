#!/usr/bin/env python3
"""Validate the wiki: frontmatter, headings, fences, links and navigation."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"

REQUIRED_KEYS = (
    "title",
    "slug",
    "part",
    "audience",
    "level",
    "applies_to",
    "collections",
    "security_impact",
    "last_reviewed",
    "owners",
)

NO_SOURCES = {"index.md", "start/glossary.md"}
NO_RELATED = {"index.md"}
LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]+)\)")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    return parts[1], parts[2]


def frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, re.MULTILINE)
    return match.group(1).strip() if match else ""


def strip_fences(body: str) -> str:
    """Remove fenced code blocks so comments and links inside code are ignored."""
    result: list[str] = []
    fence: str | None = None
    for line in body.splitlines():
        stripped = line.lstrip()
        if fence is None:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fence = stripped[:3]
                continue
            result.append(line)
        elif stripped.startswith(fence):
            fence = None
    return "\n".join(result)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    pages = sorted(DOCS.rglob("*.md"))
    nav_text = MKDOCS.read_text(encoding="utf-8") if MKDOCS.exists() else ""
    slugs: dict[str, str] = {}
    total_words = 0

    for page in pages:
        rel = page.relative_to(DOCS).as_posix()
        text = page.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(text)

        if frontmatter is None:
            errors.append(f"{rel}: missing YAML frontmatter")
            frontmatter = ""

        for key in REQUIRED_KEYS:
            if not frontmatter_value(frontmatter, key):
                errors.append(f"{rel}: missing frontmatter key '{key}'")

        slug = frontmatter_value(frontmatter, "slug").strip('"')
        if slug:
            if slug in slugs:
                errors.append(f"{rel}: duplicate slug '{slug}' (also {slugs[slug]})")
            slugs[slug] = rel

        visible = strip_fences(body)
        h1 = [line for line in visible.splitlines() if line.startswith("# ")]
        if len(h1) != 1:
            errors.append(f"{rel}: expected exactly one H1, found {len(h1)}")

        fence_count = sum(1 for line in body.splitlines() if line.lstrip().startswith("```"))
        if fence_count % 2:
            errors.append(f"{rel}: unbalanced code fences ({fence_count})")

        headings = [line for line in visible.splitlines() if line.startswith("## ")]
        if len(headings) < 5:
            warnings.append(f"{rel}: only {len(headings)} H2 sections")

        has_sources = any("Источники" in line for line in headings)
        if not has_sources and rel not in NO_SOURCES:
            errors.append(f"{rel}: missing 'Источники' section")

        has_related = any("Связанные страницы" in line for line in headings)
        if not has_related and rel not in NO_RELATED:
            warnings.append(f"{rel}: missing 'Связанные страницы' section")

        for match in LINK_RE.finditer(visible):
            target = match.group(2).strip()
            if target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            target = target.strip("<>").split("#", 1)[0]
            if not target:
                continue
            resolved = (page.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{rel}: broken link '{target}'")

        if rel not in nav_text:
            warnings.append(f"{rel}: not listed in mkdocs.yml nav")

        words = len(body.split())
        total_words += words
        print(f"{rel:48} {words:5} words")

    print(f"\nPages: {len(pages)}; words: {total_words}")
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("\nOK: structure and local links are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
