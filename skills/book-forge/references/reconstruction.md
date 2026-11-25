# Reconstruction — an existing manuscript, from the text back to a bible

This file opens in phase `bible` for `work_mode` `complete`, `revise` or `restyle`, the moment `references/ingest.md` has registered the chapters: `chapters` is no longer `[]`, every entry carries `status: "imported"` and `origin: "imported"`, and the phase still has not moved (resume resolution rule 9 of `references/state.md`). Ingestion transported the text; this file reads it back into the artefacts the rest of the pipeline needs — a canon, a plan, an index and, per mode, a revision plan or a pilot.

`references/bible.md` is the creation track and stays the authority for what a bible and an outline contain; the difference is direction. There the canon is invented out of an intention, here it is recovered from prose that already exists. Nothing in this track is allowed to invent: every line of the reconstructed bible must be traceable to a passage of the manuscript or to an answer the user gave, and where the two disagree the disagreement is reported, never smoothed over.

The rule that governs the whole file: the book is never read in one context. Its chapters arrive one at a time, in order, through dispatches that each see only their own chapter plus the accumulated notes and the provisional index — which is how chapter 12 can be read in full knowledge of chapter 04's facts without chapter 04 ever being loaded again.

## When this track runs

Three modes reach this file, and each asks something different of the same reconstructed material.

- `complete` — a partial manuscript with chapters 1..M already written. The reconstruction recovers their canon and their plan, and the same artefacts then have to be extended to the chapters M+1..N the user still wants. The re-read rule is asymmetric by design: chapters 1..M are read to be stabilized, chapters M+1..N are written against what the reconstruction produced.
- `revise` — a finished book that needs fixing. Every chapter is read, no chapter is added, and the reconstruction ends with a plan of intervention rather than with a drafting queue.
- `restyle` — a finished book whose content holds and whose voice must change. The canon, the facts and the ledger survive; the old style guide does not, and the new voice comes from the interview, not from the manuscript.

What ingestion guarantees is only this: `manuscript/NN-slug.md` exists per chapter, contiguous from `01`, registered in `meta.json`. The conversion work, the split proposal and the user's confirmation of the boundaries are all done before this file starts, and none of them is repeated here. If the chapter files are missing or their numbering is not contiguous, the project is not in this phase yet — go back to `references/ingest.md` and finish it.

The track produces, in this order: the diagnostic sweep, which extracts rather than judges; `research/reconstruction-notes.md`, which accumulates what the sweep found; the reconstructed `bible.md` and `outline.md`, assembled from those notes; the populated `continuity/` folder; and the mode-specific artefact — the stabilization sequence on `complete`, `revision-plan.md` on `revise`, `pilot.md` on `restyle`. Gate 1 is the end of all of it, and it is granted by the user alone.

## Diagnostic sweep

The sweep is a sequence of dispatches, never one dispatch over a book. `one chapter per dispatch`, in chapter order from `01` to the last imported chapter, each with a fresh context: the Researcher role from `references/roles/researcher.md`, pasted into the prompt with the input paths for that chapter, following the dispatch rule in `SKILL.md`. A dispatch that returns the canon of three chapters has been given too much, and a dispatch that returns a rewrite of its chapter has misread the role.

Each dispatch receives exactly three inputs:

- the current chapter file, `manuscript/NN-slug.md`, and nothing earlier in the manuscript;
- `continuity/facts-index.md` as it stands at that moment — the cumulative index, whose rows are still `PROVISIONAL`;
- `research/reconstruction-notes.md` — the notes extracted from the chapters already swept.

That trio is the whole context-economy design of this track: the notes and the provisional index carry forward everything earlier chapters established, so chapter 12 knows what chapter 04 settled without chapter 04 being loaded a second time, and without the sweep ever depending on one context surviving from the first chapter to the last. A dispatch whose prompt would need the previous chapter's text to make sense is a sign the notes are too thin — thicken the notes, never the context.

From its one chapter, each dispatch extracts and appends:

- canon — the characters, places, world rules or core concepts the chapter establishes, in the field vocabulary of the template that `genre_profile` selects in `references/bible.md`;
- the glossary — the terms the book uses for its own concepts, with the sense each carries in the prose;
- facts-index rows in the ledger's exact table format, cited from `references/ledger.md` and never re-invented here: one row per fact, the `F` plus three-digit ID continuing the index's own numbering, `[ch.NN]` provenance for the chapter that established it, and `Status` = `provisional` for the duration of the sweep;
- a purpose and beat summary of the chapter — why it exists in the book and what it turns — which is what `outline.md` is assembled from;
- the handoff window content for the chapter, in the five-block form `references/ledger.md` defines, so the last K imported chapters leave the sweep with handoffs already written;
- style observations — how the chapter sounds, with two or three sample sentences quoted as evidence, never as instruction;
- contradictions, as they emerge.

Contradictions are the reason the sweep is worth running chapter by chapter. When chapter 12 says something chapter 04 denied, the dispatch records both versions with both provenances — `[ch.04]` says X, `[ch.12]` says Y — and moves on. The sweep REGISTERS contradictions and never resolves them: a resolved contradiction is a canon decision, canon decisions belong to the user, and a subagent that picks the more plausible version has silently rewritten the book. They surface at Gate 1 for the user to rule on, or later through the contradiction protocol of `references/passes.md` when a pass uncovers one the sweep could not see.

`PROVISIONAL` is a status, not a mood: every row the sweep adds stays `provisional` until the user validates the reconstructed bible at Gate 1, and only then does it become `canon` or `superseded` (the carve-out is declared in `references/ledger.md`, which owns the rule; this file only uses it).

The sweep writes no prose, edits no chapter, fixes no typo and improves no sentence. Its durable output is `research/reconstruction-notes.md` plus index rows plus handoff files: everything Gate 1 will be decided on is on disk before the bible is assembled.

## The rebuilt bible

The assembly happens once, after the last chapter is swept, and it reads ONLY `research/reconstruction-notes.md` and the provisional index — never the chapters again, neither wholesale nor in slices. If the notes cannot support a field, the notes are incomplete: the answer is a targeted re-dispatch over the chapter that should have supplied it, not a re-read of the manuscript.

The reconstructed `bible.md` uses the template of `references/bible.md` for the project's `genre_profile` as its schema, filled field by field, with the mandatory `[min]` fields the ones that must be present before Gate 1 and `[opt]` fields left honestly empty when the book never supplied them. The bible is a contract, not a summary: no scene, no dialogue, no sample chapter, and no sentence whose only source is the assembler's impression of the book.

One field is different here, and the difference is the point of the whole track. The style guide of the creation track is normative — it prescribes how the book must sound. The rebuilt one is a `descriptive style guide`: it says how this book sounds NOW, with real extracts from the manuscript as few-shot evidence, because that is the only honest thing to say about prose the user has already written. It does not command, it reports; and it is published with an explicit warning that a `normative` guide does not exist yet — the normative one is born at Gate 1, out of the user's validation, and not a moment earlier. Presenting a description as a prescription is how a user ends up held to a voice they never chose.

Alongside the bible, and from the same notes, the assembly produces:

- `outline.md` for the imported chapters 1..M, one section per chapter in the exact heading shape and the five blocks of `references/bible.md`, built from the purpose and beat summaries of the sweep. On `complete` it covers 1..M only; chapters M+1..N are added at Gate 1, from the interview;
- `continuity/window/` — handoff files for the last K imported chapters, K from `continuity_window` in `meta.json`, as `references/ledger.md` requires for an imported manuscript: the tail of chapters 1..M, so the first drafting dispatch after M starts with handoff context instead of an empty folder.

Nothing assembled here is canon before Gate 1. It is a proposal in the shape of the final artefacts, and it is presented as such: what the user is being asked to approve is a reading of their own book, and the correction loop runs through the Researcher until they recognise it.

## Mode complete — Gate 1 and stabilization

Gate 1 on `complete` validates two things and approves a third, and the order matters.

The user validates the reconstructed bible — "is this the book you wrote?" — and that validation is what turns the `descriptive style guide` `normative`: either the user accepts the voice the manuscript actually has, and the description becomes the rule, or they tell you where the book is NOT what they wanted, and the correction enters the guide before it is fixed. This is the specification's own contract (objective 3), and it is the only route from description to prescription: never promote a descriptive guide by yourself, and never describe prose as canonical because it was written first.

With the bible validated, the user approves `outline.md`, which now has to cover both halves of the book: the existing chapters 1..M, whose contracts the sweep reconstructed, and the new chapters M+1..N, whose contracts are built with the user in the interview that `references/intake.md` opened — one question at a time, the missing table of contents integrated into the conversation rather than invented. The outline is one document; a book whose existing half is traced and whose new half is guessed is not approved.

Then STABILIZATION, and it is mandatory: before the first new chapter is written, the `structure and continuity` passes run over the imported chapters 1..M, and only those two. The engine is `references/passes.md`, cited here and not restated, with its macro→micro order and its registries; style, grammar and spelling are deliberately excluded, because they belong to phase 3 over the whole book, once the new chapters exist and the text has stopped moving. Stabilizing an imported manuscript means making it structurally and factually sound enough that a new chapter can be drafted against it — not editing the prose the user already accepted.

The bookkeeping order is fixed and invariant C5 enforces it:

- the stabilization passes run to completion over 1..M;
- the orchestrator then registers chapters M+1..N in `meta.json.chapters`, each with `status: "planned"` and `origin: "written"`, and sets both `stabilization` fields to `done`;
- ONLY THEN does `phase` become `"chapters"`.

Drafting a new chapter before stabilization is `done` is a state the machine rejects (C5), and it is also the mistake the rule exists to prevent: a chapter M+1 written against an unstabilized book inherits every contradiction and every broken structure of chapters 1..M, and the cost of fixing it later is the whole book.

## Mode revise — Gate 1 and the revision plan

Gate 1 on `revise` has three approvals, and all three are the user's.

First the bible: the same validation as on `complete`, the same consequence — the `descriptive style guide` becomes `normative` when the user accepts the current voice or states where the book is not what they wanted. The bible is the canon every editor dispatch reads, so it is validated before anything is planned against it.

Then `outline.md`, reconstructed for the whole book: one section per chapter, what each chapter is for and what it promises, as it is now. A revision plan written against an outline nobody checked is a plan against a different book.

Then `revision-plan.md` at the project root, in the pinned format:

- per selected pass — one block for each pass the user wants to run, in macro→micro order;
- for each pass, its purpose — what this pass is expected to achieve on this book;
- for each pass, per-chapter notes — where to intervene and why, chapter by chapter, specific enough that the editor dispatched on that chapter knows what it is looking for;
- for each pass, what NOT to touch — the passages, chapters or effects that must survive the revision untouched, named explicitly. The do-not-touch list is the part of the plan that keeps a revision from becoming a rewrite, and it is as binding as the instructions.

`pass_scope` is derived from the approved plan and from nothing else: a subset of `structure, continuity, style, grammar, spelling`, in macro→micro order, written at Gate 1 (invariant C6 of `references/state.md`). A pass in `pass_scope` that the plan does not cover, or a plan block whose pass is missing from the scope, is an inconsistency to resolve with the user before approval, not after.

Approval writes the gate and moves `phase` to `"passes"`. No chapter is ever `status: "planned"` in this mode: the whole book already exists as `imported`, and C7 rejects a `planned` chapter past phase `chapters` in any case. What a pass changes in `meta.json` is the chapter gates, not the nature of the chapters.

## Mode restyle — new voice and the pilot

`restyle` keeps the book and replaces its voice. The intake interview has already established what the user wants instead of the current register — that answer, not the description of the manuscript, is what fills the style guide, and it is `normative` from the moment it is written: a rule the user stated is a rule, and it needs no Gate 1 promotion to be obeyed. Gate 1 validates that bible — the canon plus the new guide, with no trace of the old one — and approves the pilot; present the two together, the bible first, as `references/bible.md` requires of every Gate 1.

The constitutional constraint of this mode is that `the old book releases only canon, facts and ledger`. What crosses from the old book into the new one is what it asserts, not how it sounds: the bible's canon fields, the facts index, the handoff window and the glossary of terms. The old style guide NEVER enters — not as a starting point, not as a "current voice" section, not as few-shot examples of what to avoid. The descriptive observations the sweep wrote stay in `research/reconstruction-notes.md` as research, and they do not become the bible's guide; the bible's guide is the new voice, and the two voices are never presented side by side as if the user had to choose.

The pilot is the proof that the new voice works, and it precedes the whole restyle. Take one chapter — or a long extract where a chapter is unwieldy — and dispatch it to the Copy-editor role, `references/roles/copy-editor.md`, as a style and voice pass. Its inputs are exactly three: the chosen chapter or extract, the NEW normative style guide from the bible, and the canon and facts extracted from the ledger for that chapter. Nothing else of the old book: no other chapter, no old guide.

The round-trip is the point: the rewritten pilot comes back, you show it to the user in their language, they react, the guide is adjusted if their reaction exposes a gap, and the dispatch runs again. The loop ends when the user approves the pilot at Gate 1 — silence is not approval, and a pilot that looks convincing to you is not approval either. The approved rewrite is saved as `pilot.md` at the project root, and from then on it is the few-shot anchor of EVERY style pass dispatch on this book: the concrete answer to "what does the new voice sound like", carried as an example rather than as a paragraph of adjectives.

`pass_scope` on `restyle` is exactly `style, continuity, grammar, spelling` — style first, by design, because the voice is the change (C6). Gate 1 writes the gate, and `phase` moves to `"passes"`. As on `revise`, no chapter is `planned`: the book is entirely imported, and the passes rewrite it in place, one pass at a time.
