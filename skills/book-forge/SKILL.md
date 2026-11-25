---
name: book-forge
description: Write or revise a full book manuscript — novel or nonfiction — from an idea or an existing draft to an exportable EPUB/DOCX. Use when the user wants to write a book, continue or complete a partial manuscript, correct and professionally edit an existing book (even one written without this skill), or restyle a finished book with a new voice.
---

book-forge takes a person who has a book in their head and produces a finished manuscript on disk, chapter by chapter, with a human gate at every step. It self-reveals one of four jobs in the first conversation — create a book from scratch, complete a partial manuscript, correct an existing book (even one written before this skill existed), or restyle a finished book with a new voice — and runs the same underlying machine for all four.
It produces plain markdown in the user's book project (bible, outline, one file per chapter, continuity ledger, pass registries), then an EPUB 3 that Kindle Create accepts and an optional .docx.
It stops at export: no KDP upload, no cover, no marketing.

## First action — read the state

Never start work from the conversation alone. If `<project>/meta.json` exists, read it first, then `references/state.md` for the transition rules, then the reference file of the current phase: Read `references/<phase>.md` and follow it.
`<phase>` is always resolved through the phase × work_mode routing table below, never from the literal field value: `final_review` maps to `final-review.md`; `bible` on an existing manuscript maps to `references/ingest.md` while no chapter is imported and to `reconstruction.md` once chapters are registered.
Resolve and re-read those files at every session, including a resume after months: never trust session memory — the disk is the state.
If `<project>/meta.json` is missing, the project has not started: open `references/intake.md` (phase 0) and run the interview.
If the user has no project directory yet, ask where to create it (or which existing directory to open) before any other action.

## Phase machine

| phase | reference file | gate | executors |
|---|---|---|---|
| `intake` | `references/intake.md` | the phase-0 questions are answered (work_mode, genre profile, audience, promise, voice, language, target length, validation blocks) | inline (Interviewer) |
| `bible` | `references/bible.md` on create · `references/ingest.md` on an existing manuscript with `chapters == []` · `references/reconstruction.md` on an existing manuscript with imported chapters | `gates.bible_approved` (Gate 1: the user validates the bible/outline, or the reconstructed bible plus the revision plan) | Researcher subagent + user; existing-book work starts in `references/ingest.md` and continues in `reconstruction.md` as soon as the chapters are imported |
| `chapters` | `references/drafting.md` | the user reads and approves each chapter (or each block of N chapters) before the next one starts | Drafter subagent, main agent orchestrating only |
| `passes` | `references/passes.md` | `gates.passes_approved`, granted through protocol (b): registries and diffs controlled and sampled, full re-read always available | editor subagents — one pass at a time, one file at a time |
| `final_review` | `references/final-review.md` | `gates.final_approved` | a fresh Final-reviewer per chapter, then the user |
| `export` | `references/export.md` | none — pandoc runs and the exports land in `exports/` | inline + pandoc |
| `done` | terminal: nothing left to run | none | none |

Move `phase` forward only when its gate is satisfied; the exact `meta.json` fields and the transition rules live in `references/state.md`.

## Routing by work_mode

| work_mode | intake | bible | chapters | passes | final_review | export |
|---|---|---|---|---|---|---|
| `create` | yes | yes — `references/bible.md`, then Gate 1 | yes, 1..N | yes, after the drafting | yes | yes |
| `complete` | yes | yes — `references/ingest.md` → `reconstruction.md` on 1..M, Gate 1 | yes, M+1..N | yes, on the whole book after the drafting | yes | yes |
| `revise` | yes | yes — `references/ingest.md` → `reconstruction.md` plus the revision plan, Gate 1 | no | yes — this is the main work | yes | yes |
| `restyle` | yes | yes — `references/ingest.md` → `reconstruction.md`, releasing ONLY canon, facts and ledger (never the old style guide), plus the rewritten pilot, Gate 1 | no | yes — style/voice → continuity → grammar → spelling | yes | yes |

Stabilization (`complete`): structure and continuity run on chapters 1..M BEFORE chapter M+1 is drafted; style, grammar and spelling stay in phase 3, over the whole book.
Restyle: the approved pilot is kept as the few-shot anchor for every style pass, and phase 3 closes with style/voice → continuity → grammar → spelling.

## Dispatching roles

Every subagent dispatch (W1) pastes into the prompt the path of its role file and the input files for that specific task — never the whole book, never a paraphrase of the role:

| role | prompt file |
|---|---|
| Researcher | `references/roles/researcher.md` |
| Drafter | `references/roles/drafter.md` |
| Structure-editor | `references/roles/structure-editor.md` |
| Continuity-checker | `references/roles/continuity-checker.md` |
| Copy-editor (one pass at a time) | `references/roles/copy-editor.md` |
| Final-reviewer | `references/roles/final-reviewer.md` |

Harness mapping: on pi use the subagent tool, on Claude Code the Task tool, with no subagent tool available run the role inline in the same order.
Two protected exceptions: at the end of phase 3 the final gate writes `awaiting_fresh_session` into `meta.json` and stops hard — the gate runs in a new session, and a self-review is allowed only on an explicit user override, reported as `degraded_non_independent`; a Researcher without web access declares the limit immediately and works from the user's own material.
Interview rule: one question at a time, in the user's language, until the phase-0 questions are complete.
Ingest rule: after the file conversion the agent proposes the split and the user confirms the chapter split before any reconstruction starts.

## Never

- Advance a chapter to the next one without the human gate of reading and approval.
- Load the whole book into one context; work file by file against the compressed continuity ledger.
- Quote text from an external source without its source, or rewrite a concept in other words unless the user asked for it explicitly.
- Let a subagent write `meta.json`, `bible.md` or the continuity ledger outside its contract.
- Trust session memory instead of the files on disk.
- Go past the export: no KDP upload, no cover design, no marketing.
