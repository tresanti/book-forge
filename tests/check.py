#!/usr/bin/env python
"""Structural checks for the book-forge skill repository.

Core = stdlib only. Task 4 adds JSON-Schema validation (jsonschema,
declared in pyproject.toml) and Task 13 adds role-path integrity.
Run: uv run tests/check.py  — exit 1 lists every problem.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---- expectations registry (grow with tasks; exact values are binding) ----

REQUIRED_FILES: list[str] = [
    "skills/book-forge/SKILL.md",
    "skills/book-forge/references/state.md",
    "skills/book-forge/references/intake.md",
]

REQUIRED_HEADERS: dict[str, list[str]] = {
    # "repo/relative.md": ["## Exact header", ...]
    "skills/book-forge/SKILL.md": [
        "## First action — read the state",
        "## Phase machine",
        "## Routing by work_mode",
        "## Dispatching roles",
        "## Never",
    ],
    "skills/book-forge/references/state.md": [
        "## meta.json — fields",
        "## Transition rules",
        "## Project directory layout",
        "## Naming and language rules",
        "## Resuming a project",
    ],
    "skills/book-forge/references/intake.md": [
        "## Protocol",
        "## Step 1 — identify the job",
        "## Step 2 — validation mode (ask first)",
        "## Core questions (all profiles)",
        "## Question topics — fiction",
        "## Question topics — practical nonfiction",
        "## Question topics — narrative nonfiction",
        "## Raw material",
        "## Online research",
        "## Write meta.json",
    ],
}

REQUIRED_SUBSTRINGS: dict[str, list[str]] = {
    "skills/book-forge/SKILL.md": [
        "Read `references/<phase>.md`",
        "never trust session memory",
        "references/roles/researcher.md",
        "references/roles/drafter.md",
        "references/roles/structure-editor.md",
        "references/roles/continuity-checker.md",
        "references/roles/copy-editor.md",
        "references/roles/final-reviewer.md",
        "references/ingest.md",
        "awaiting_fresh_session",
        "degraded_non_independent",
        "one question at a time",
        "user confirms the chapter split",
    ],
    "skills/book-forge/references/state.md": [
        "written only by the orchestrator",
        "references/<phase>.md",
        "continuity_window",
        "meta.schema.json",
    ],
    "skills/book-forge/references/intake.md": [
        "one question at a time",
        "in the user's own language",
        "create | complete | revise | restyle",
        "validation_mode",
        "web_available",
    ],
}

FRONTMATTER_LINES: dict[str, list[str]] = {
    "skills/book-forge/SKILL.md": ["name: book-forge"],
}
DESCRIPTION_MAX = 1024

SCHEMA_PATH = "skills/book-forge/references/meta.schema.json"
FIXTURES_VALID: list[str] = [
    "tests/fixtures/meta-create-intake.json",
    "tests/fixtures/meta-create-chapters.json",
    "tests/fixtures/meta-complete-bible.json",
    "tests/fixtures/meta-revise-passes.json",
    "tests/fixtures/meta-restyle-final-review.json",
    "tests/fixtures/meta-revise-done.json",
]
FIXTURES_INVALID: list[str] = [
    "tests/fixtures/meta-invalid-bad-enum.json",
    "tests/fixtures/meta-invalid-block-size.json",
    "tests/fixtures/meta-invalid-gates.json",
    "tests/fixtures/meta-invalid-file-number.json",
    "tests/fixtures/meta-invalid-flags.json",
    "tests/fixtures/meta-invalid-scope.json",
]
PASS_ORDER = ["structure", "continuity", "style", "grammar", "spelling"]

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


def check_meta_invariants(meta: dict) -> list[str]:
    """Cross-field rules JSON Schema cannot express. Contract mirrored in
    references/state.md — keep the two in sync."""
    errs: list[str] = []
    phase = meta.get("phase")
    gates = meta.get("gates", {})
    flags = meta.get("flags", {})
    mode = meta.get("work_mode")
    chapters = meta.get("chapters", [])

    # C1 chapter numbering: contiguous ascending from 1, file prefix matches
    numbers = [c.get("number", -1) for c in chapters]
    if numbers != list(range(1, len(numbers) + 1)):
        errs.append("chapters: numbers must be contiguous ascending from 1")
    for c in chapters:
        if not str(c.get("file", "")).startswith(f"manuscript/{c.get('number', 0):02d}-"):
            errs.append(f"chapters: file {c.get('file')!r} does not match number {c.get('number')}")

    # C2 phase-gate coupling — no phase advance without user gates
    if phase in ("chapters", "passes", "final_review", "export", "done") and not gates.get("bible_approved"):
        errs.append("phase beyond 'bible' requires gates.bible_approved")
    if phase in ("final_review", "export", "done") and not gates.get("passes_approved"):
        errs.append("phase beyond 'passes' requires gates.passes_approved")
    if phase in ("export", "done") and not gates.get("final_approved"):
        errs.append("phase beyond 'final_review' requires gates.final_approved")

    # C3 conflicting stop states
    if flags.get("awaiting_fresh_session") and flags.get("degraded_non_independent"):
        errs.append("flags: awaiting_fresh_session and degraded_non_independent are mutually exclusive")

    # C4 web availability must be probed by end of intake
    if phase != "intake" and flags.get("web_available") is None:
        errs.append("flags.web_available must be true/false once past intake")

    # C5 stabilization bookkeeping (work_mode complete only)
    stab = meta.get("stabilization")
    if mode == "complete":
        if not stab:
            errs.append("work_mode 'complete' requires a stabilization block")
        elif phase in ("chapters", "passes", "final_review", "export", "done") and (stab.get("structure") != "done" or stab.get("continuity") != "done"):
            errs.append("mode complete: drafting new chapters requires stabilization done on imported chapters")
    elif stab is not None:
        errs.append("stabilization block is only valid for work_mode 'complete'")

    # C6 pass scope: mode-specific contracts; progress mirrors
    # (create/complete: full macro->micro set; revise: any non-empty subset in
    #  macro->micro order; restyle: exactly [style, continuity, grammar,
    #  spelling] — style/voice first by design, spec W4; the equality checks
    #  pin the order, so the sorted-index check applies to revise subsets only)
    scope = meta.get("pass_scope")
    if scope is not None:
        progress = meta.get("pass_progress")
        if progress is not None and set(progress) != set(scope):
            errs.append("pass_progress keys must mirror pass_scope")
        if not set(scope) <= set(PASS_ORDER):
            errs.append("pass_scope contains unknown passes")
        elif mode == "revise":
            idx = [PASS_ORDER.index(p) for p in scope]
            if idx != sorted(idx):
                errs.append("pass_scope violates macro->micro order: " + " -> ".join(PASS_ORDER))
        elif mode in ("create", "complete"):
            if scope != PASS_ORDER:
                errs.append("work_mode create/complete requires the full pass scope")
        elif mode == "restyle":
            if scope != ["style", "continuity", "grammar", "spelling"]:
                errs.append("work_mode 'restyle' requires pass_scope = style, continuity, grammar, spelling")

    # C7 drafting statuses only during phase 'chapters'; nothing may stay
    # 'planned' (unwritten) once the manuscript is past the chapter cycle
    for c in chapters:
        if c.get("status") in ("drafting", "user_review") and phase != "chapters":
            errs.append(f"chapters: status {c.get('status')!r} valid only in phase 'chapters'")
        if c.get("status") == "planned" and phase in ("passes", "final_review", "export", "done"):
            errs.append("chapters: status 'planned' is not valid beyond phase 'chapters'")

    # C8 imported work must record its chapters — from Gate 1 on: during
    # phase 'bible' (pre-split ingestion) chapters may legitimately be []
    if mode in ("complete", "revise", "restyle") and (phase not in ("intake", "bible") or gates.get("bible_approved")) and not chapters:
        errs.append("imported work_mode with no chapters recorded")

    return errs


def check_schema(errors: list[str]) -> None:
    import jsonschema

    schema_path = ROOT / SCHEMA_PATH
    if not schema_path.is_file():
        errors.append(f"missing file: {SCHEMA_PATH}")
        return
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema)
    for rel in FIXTURES_VALID + FIXTURES_INVALID:
        if not (ROOT / rel).is_file():
            errors.append(f"missing fixture: {rel}")
            continue
        instance = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        schema_errs = [e.message for e in validator.iter_errors(instance)]
        inv_errs = check_meta_invariants(instance)
        if rel in FIXTURES_VALID and (schema_errs or inv_errs):
            errors.extend(f"{rel}: {m}" for m in schema_errs + inv_errs)
        elif rel in FIXTURES_INVALID and not (schema_errs or inv_errs):
            errors.append(f"{rel}: fixture must be INVALID but validates")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_frontmatter(errors)
    check_headers(errors)
    check_substrings(errors)
    check_links(errors)
    check_schema(errors)
    if errors:
        print(f"FAIL — {len(errors)} problem(s)")
        for e in errors:
            print(f" - {e}")
        return 1
    print("OK — all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
