# State — the meta.json contract

`meta.json` sits at the root of every book project and is the single source of truth for the pipeline state: the disk is the state, never session memory.
The machine authority is `references/meta.schema.json` (JSON Schema draft 2020-12): a project's `meta.json` is valid only when it validates against that schema. The cross-field rules JSON Schema cannot express are invariants C1–C8, spelled out as the transition rules below and pinned over `meta.json` fixtures by the skill's own test harness. This file mirrors the contract for the agent; when the two disagree, `meta.schema.json` and the invariants win.

## meta.json — fields

Every field is written by the orchestrator — see rule (1). Unknown properties are rejected: `meta.schema.json` closes every object with `additionalProperties: false`.
Required: `schema_version`, `project`, `work_mode`, `genre_profile`, `validation_mode`, `phase`, `flags`, `gates`, `chapters`, `continuity_window`. Everything below marked optional may be absent.

| field | type / values | when it is written |
|---|---|---|
| `schema_version` | `1` (constant) — contract revision, bumped only if the schema changes | project creation |
| `project.title` | string, at least 1 character — the book title as the user writes it | creation, from the interview |
| `project.slug` | kebab-case ASCII, `^[a-z0-9]+(-[a-z0-9]+)*$` | creation |
| `project.language` | language tag, `^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$` (`en`, `it`, `pt-BR`) | creation, from the interview |
| `project.created` | ISO date `YYYY-MM-DD` | creation |
| `work_mode` | `create` · `complete` · `revise` · `restyle` | end of intake |
| `genre_profile` | `fiction` · `practical_nonfiction` · `narrative_nonfiction` | end of intake |
| `validation_mode.type` | `chapter` · `blocks` | end of intake |
| `validation_mode.block_size` | integer ≥ 2 — the block of N chapters validated together; required when `type` is `blocks` | end of intake, when `type` is `blocks` |
| `phase` | `intake` · `bible` · `chapters` · `passes` · `final_review` · `export` · `done` | on every gate (rule 2) |
| `flags.awaiting_fresh_session` | boolean — `true` stops the pipeline until a genuinely new session picks it up (rule 3) | end of phase 3, and again on a final-gate rejection |
| `flags.degraded_non_independent` | boolean — `true` records a self-review the user explicitly accepted (rule 3) | when the user overrides the fresh session |
| `flags.web_available` | `true` · `false` · `null` — `null` is legal only during `intake` (rule 4) | end of intake |
| `gates.bible_approved` | boolean — Gate 1: the user approved the bible and outline, or the reconstructed bible plus the revision plan | Gate 1 |
| `gates.passes_approved` | boolean — the user approved the pass registries through protocol (b) | end of phase 3 |
| `gates.final_approved` | boolean — the user approved the final review report | final gate |
| `chapters` | array of chapter objects; legitimately `[]` until the chapter split is confirmed | on split confirmation, then at every chapter gate |
| `chapters[].number` | integer 1–99, contiguous ascending from 1 | when the chapter enters the plan |
| `chapters[].file` | `manuscript/NN-slug.md`, `^manuscript/\d{2}-[a-z0-9]+(-[a-z0-9]+)*\.md$` | when the chapter enters the plan |
| `chapters[].title` | string — the chapter title | when the chapter enters the plan |
| `chapters[].status` | `planned` · `imported` · `drafting` · `user_review` · `approved` (rule 5) | at every chapter gate |
| `chapters[].origin` | `written` · `imported` | when the chapter enters the plan |
| `continuity_window` | integer 2–10, default `3` — K, how many approved chapter handoffs the drafter sees | creation; changed only on an explicit user request |
| `length_target` | optional object or `null`: `words` and `chapters`, each integer or `null` | end of intake, when the user gives a target |
| `stabilization` | optional object, `work_mode: complete` only: `structure` and `continuity`, each `pending` · `in_progress` · `done` (rule 6) | before phase `chapters` |
| `pass_scope` | optional array, at least 1 unique item from `structure` · `continuity` · `style` · `grammar` · `spelling` (rule 7) | Gate 1 for `revise`; before phase `passes` otherwise |
| `pass_progress` | optional object keyed by the `pass_scope` passes — each `pending` · `in_progress` · `done`, at least 1 key; its keys always mirror `pass_scope` | throughout phase `passes` |
| `notes` | optional string — free-form notes on overrides and user decisions | whenever a decision needs to survive the session |

The `continuity_window` default is `3`; the schema range is 2–10.

## Transition rules

1. `meta.json` is written only by the orchestrator — never by a subagent. Subagents return findings, diffs and handoffs; the orchestrator records them in the state file.
2. Advance `phase` only through the gates of invariant C2: `gates.bible_approved` before `chapters` or `passes`; `gates.passes_approved` before `final_review`; `gates.final_approved` before `export`. A phase past its gate is an invalid state, not a shortcut.
3. `awaiting_fresh_session: true` blocks EVERYTHING until the pipeline resumes in a NEW session. A session recognises itself as fresh when it has run no drafting or editing turn on this book in its own context; only then does it set `awaiting_fresh_session: false` and start the review. Inline, with long books, the review dispatches may be split across several consecutive fresh sessions. A self-review is allowed only on an explicit user override and is recorded as `degraded_non_independent: true` — the two flags are never both `true` (C3).
4. `web_available` is established by the end of intake as `true` or `false`; `null` is legal only during `intake` (C4).
5. Chapter lifecycle: `planned` or `imported` → `drafting` → `user_review` → (corrections → `drafting`) → `approved`. `drafting` and `user_review` exist only in phase `chapters`, and `planned` — a chapter never written — is forbidden from `passes` onward (C7).
6. `work_mode: complete` requires a `stabilization` block whose `structure` and `continuity` both reach `done` over the imported chapters 1..M before phase `chapters`; it never rolls back and stays `done` in every later phase (C5). A `stabilization` block on any other work_mode is invalid.
7. `pass_scope` and `pass_progress` are bound to the work_mode (C6): `create`/`complete` = all five passes in macro→micro order (`structure → continuity → style → grammar → spelling`); `revise` = any non-empty subset in that same macro→micro order, fixed by the revision plan at Gate 1; `restyle` = exactly `style, continuity, grammar, spelling` (style/voice leads the remaining queue by design, spec W4). `pass_progress` always carries exactly the `pass_scope` keys.
8. Once a gate field is set it is never rolled back without an explicit user decision. The one planned controlled rollback: a chapter rejected at the final gate → explicit user confirmation → `phase: "passes"` with `gates.passes_approved: false` → a targeted pass on that chapter plus `resync facts-index` → a new Gate (b) → a new entry into `final_review` (inline, `awaiting_fresh_session` goes back to `true`: the session has now edited prose).
9. `<phase>` in the resume rule is ALWAYS resolved through this phase × work_mode table, never from the literal field value (`final_review` maps to `final-review.md`):
   - `intake` → `references/intake.md`
   - `bible` → `references/bible.md` on `create` | `references/ingest.md` on existing work with `chapters == []` | `references/reconstruction.md` on existing work with imported chapters
   - `chapters` → `references/drafting.md`
   - `passes` → `references/passes.md`
   - `final_review` → `references/final-review.md`
   - `export` / `done` → `references/export.md` — `done` is terminal for the operator (nothing left to run), but the resolver still maps it here because a re-export is always legal
10. `notes` carries decisions and context — scope choices, limitations, deferred items — never progress claims, and never a substitute for evidence: the pipeline's state lives in the files (reports, registries, meta fields), and a gate is read from those files, not from any narrative note. Both flags stay report-visible, never note-declared: `awaiting_fresh_session` and `degraded_non_independent` behave exactly as stated, whatever the notes say.

## Project directory layout

```
<book-project>/
├── meta.json            # pipeline state (schema: references/meta.schema.json)
├── bible.md             # canon: premise, characters/world or concepts/promises, style guide, glossary
├── outline.md           # TOC + per-chapter contract
├── manuscript/          # 01-slug.md, 02-slug.md… one file per chapter
├── continuity/
│   ├── facts-index.md   # index of facts/entities/promises with provenance [ch.NN]
│   └── window/          # NN-slug.md — the K most recent handoffs (K = meta.continuity_window)
├── research/            # raw material; sources.md (URL + access date)
├── passes/
│   ├── registry-structure.md / registry-continuity.md / registry-style.md / registry-grammar.md / registry-spelling.md
│   └── contradiction-01.md …   # STOP files for ambiguous canon
├── reports/
│   ├── final-review/ch-NN.md   # per-chapter report
│   └── final-review.md         # aggregate report
├── revision-plan.md     # work_mode revise only — revision plan approved at Gate 1
├── pilot.md             # work_mode restyle only — rewritten pilot chapter, kept as the few-shot anchor
├── book.yaml            # export metadata (phase 5)
└── exports/             # <slug>.epub, <slug>.docx
```

## Naming and language rules

- One file per chapter: `manuscript/NN-slug.md`, `NN` two digits zero-padded, first heading `# <title>`.
- Slugs are kebab-case ASCII: accented or non-Latin titles are transliterated (`Città di nebbia` → `citta-di-nebbia`); when transliteration is not reliable, fall back to `chapter-NN`.
- Prose artefacts of the project (bible, outline, registries, reports, handoffs) are written in the book's language, `project.language`; skill keys, file names and enum values stay English.

## Resuming a project

At every session, including a resume after months: read `<project>/meta.json`, then this file for the transition rules, then re-read `references/<phase>.md` for the current phase and follow it. Resolve `<phase>` through rule (9), never from the literal field value. Never trust session memory — the disk is the state. If `meta.json` is missing the project has not started: open `references/intake.md`.
