# book-forge — maintenance backlog

Post-`v1.0.0`. Two sources: the whole-branch final review triage and a real-world coordination exercise that surfaced one behavioral gap. Nothing here blocks normal use; these are quality-of-life hardening items.

## Gap surfaced after v1.0.0 and fixed in v1.0.1

1. **Partial-gate resumption is now explicit.** An orchestrator can stop between per-chapter dispatches (crash, session limit, host handoff). The skill already refused to aggregate on missing reports, but it did not say that the reports a previous session left on disk are the work of fresh dispatches and therefore stand: the resumed session re-dispatches only the chapters whose report is missing, and never re-reviews to refresh an existing report. Fixed in `final-review.md`.
2. **Progress claims now have one home.** Pipeline progress lives in the files (reports, registries, meta fields), never in narrative notes: `meta.json.notes` carries decisions and context only. Fixed in `state.md` (transition rules).

## Hardening ideas (deferred, none blocking)

- `check_headers`/`check_substrings` are membership-only: an extra pinned-section header would pass green. Hardening: exact-set where a section's perimeter is the contract.
- Invalid-fixture assertion `len(errs)==1` (single-reason rejection is today verified by reasoning over the fixtures, not enforced by the harness).
- `check_links`: skip `.superpowers/` and `.worktrees/` inside worktrees (or iterate `git ls-files '*.md'`).
- `format_checker` on `project.created` (annotation currently not enforced).
- CI: `permissions: {}` and tighter action tags.
- Re-export reusing an existing `book.yaml` (the author field is currently asked again at every export).
- Hygiene: drop the unused `import sys` in `tests/check.py`.

## Prose polish (from the final review triage)

`SKILL.md` done/export wording vs `state.md` rule 9; `intake.md` soften the "twenty questions ceiling"; `export.md` "printable by conversion" phrasing; README tree missing `revision-plan.md`/`pilot.md`; "single declared exception" wording to reconcile with the two declared write exceptions (reconstruction sweep + phase-3 pass-local window); `drafting.md` "approved handoffs" vs imported chapters in `complete` mode.
