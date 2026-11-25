#!/usr/bin/env python
"""Structural checks for the book-forge skill repository.

Core = stdlib only. Task 4 adds JSON-Schema validation (jsonschema,
declared in pyproject.toml) and Task 13 adds role-path integrity.
Run: uv run tests/check.py  — exit 1 lists every problem.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---- expectations registry (grow with tasks; exact values are binding) ----

REQUIRED_FILES: list[str] = []

REQUIRED_HEADERS: dict[str, list[str]] = {
    # "repo/relative.md": ["## Exact header", ...]
}

REQUIRED_SUBSTRINGS: dict[str, list[str]] = {}

FRONTMATTER_LINES: dict[str, list[str]] = {
    "skills/book-forge/SKILL.md": ["name: book-forge"],
}
DESCRIPTION_MAX = 1024

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+?)\)")
URL_RE = re.compile(r"^[a-z][a-z0-9+.-]*://")
FENCE_RE = re.compile(r"`{3,}.*?`{3,}", re.DOTALL)
SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", re.DOTALL)

# ---- checks ----------------------------------------------------------------


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def check_required_files(errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing file: {rel}")


def check_frontmatter(errors: list[str]) -> None:
    for rel, required in FRONTMATTER_LINES.items():
        if not (ROOT / rel).is_file():
            continue  # reported when listed in REQUIRED_FILES
        lines = read(rel).splitlines()
        if not lines or lines[0] != "---":
            errors.append(f"{rel}: missing YAML frontmatter")
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            errors.append(f"{rel}: frontmatter not closed")
            continue
        fm = lines[1:end]
        for line in required:
            if line not in fm:
                errors.append(f"{rel}: frontmatter missing {line!r}")
        for line in fm:
            if line.startswith("description:"):
                value = line[len("description:"):].strip()
                if len(value) > DESCRIPTION_MAX:
                    errors.append(f"{rel}: description over {DESCRIPTION_MAX} chars")
                break
        else:
            errors.append(f"{rel}: frontmatter missing description")


def check_headers(errors: list[str]) -> None:
    for rel, wanted in REQUIRED_HEADERS.items():
        if not (ROOT / rel).is_file():
            continue
        have = {ln.strip() for ln in read(rel).splitlines() if ln.startswith("## ")}
        for header in wanted:
            if header not in have:
                errors.append(f"{rel}: missing heading {header!r}")


def check_substrings(errors: list[str]) -> None:
    for rel, wanted in REQUIRED_SUBSTRINGS.items():
        if not (ROOT / rel).is_file():
            continue
        text = read(rel)
        for needle in wanted:
            if needle not in text:
                errors.append(f"{rel}: missing pinned string {needle!r}")


def strip_code(text: str) -> str:
    """Drop fenced code blocks and variable-length inline code spans — the
    link-check judges prose markdown, never link examples quoted inside code
    (including double-backtick spans that quote code containing backticks)."""
    return SPAN_RE.sub(" ", FENCE_RE.sub(" ", text))


def check_links(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or "node_modules" in path.parts or "graphify-out" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for target in LINK_RE.findall(strip_code(read(rel))):
            if URL_RE.match(target) or target.startswith("/"):
                continue  # remote URLs and repo-absolute links: out of scope
            target = target.split("#", 1)[0]
            if not target:
                continue  # pure anchor
            if not (path.parent / target).is_file():
                errors.append(f"{rel}: broken link -> {target}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_frontmatter(errors)
    check_headers(errors)
    check_substrings(errors)
    check_links(errors)
    if errors:
        print(f"FAIL — {len(errors)} problem(s)")
        for e in errors:
            print(f" - {e}")
        return 1
    print("OK — all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
