# The continuity ledger — facts index and handoff window

The `continuity/` folder holds two artefacts. `continuity/facts-index.md` is the durable record: every fact the approved book has established, with the provenance that lets a later session check it. `continuity/window/` is the volatile one: one short handoff per approved chapter, kept only as far back as the drafter actually needs. The index is memory; the window is context economy.

The split is the whole design. Facts never depend on a handoff file surviving, so the window can be pruned without loss; and the window never has to carry the book, so it can stay small. A fact that exists only in a handoff is a fact you have already lost.

Both artefacts are written by the Continuity-checker, never by you: `meta.json` is your only write in this protocol, and it is the only state that decides whether a chapter is allowed to contribute facts at all.

## facts-index.md

Path: `continuity/facts-index.md`. One file per book, one table, six columns, in this exact shape:

| ID | Type | Fact or statement | Established | Source | Status |
|---|---|---|---|---|---|
| F012 | character | Mira has never left the delta | [ch.07] | manuscript/07-the-crossing.md | canon |
| F013 | promise | The locked drawer is opened in the last third | bible §Secondary arcs | bible.md | canon |

- `ID` — `F` plus a three-digit number, assigned once and never reused, never renumbered. A reader of the index finds a row by its ID; an index whose numbering shifts under edits cannot be cited, and an index that cannot be cited is a summary.
- `Type` — exactly one of `character, place, object, event, timeline, promise, term, thread`. `thread` is the open kind: foreshadowing planted and not yet paid, an obligation the prose has taken on, a constraint a later chapter must respect.
- `Fact or statement` — one verifiable sentence, in the book's language, phrased so that a chapter can be checked against it. Two facts in one row cannot be superseded separately, so they are two rows.
- `Established` — the provenance, in exactly one of two forms: `[ch.NN]` when an approved chapter established the fact (NN = the chapter number, two digits, matching `manuscript/NN-slug.md`), or `bible §<section>` when it comes from the canon — `bible §Characters`, `bible §World`. This column is the reason the file exists: a fact with no provenance is an assertion, and an editor cannot rule on an assertion.
- `Source` — the file the evidence sits in: `manuscript/NN-slug.md` for a chapter fact, `bible.md` or `outline.md` for a canonical one.
- `Status` — `canon`, `superseded` or `provisional`. `canon` is a fact currently in force. `superseded` is a fact the book has refuted or replaced, kept in place with the new row beside it. `provisional` is legal only during the diagnostic sweep described under `## Change discipline`, before the bible has been validated; it is the status the enum carries, while the row itself is spoken of as `PROVISIONAL` — added by the sweep, never by a chapter.

Append-only is the discipline of the table. Rows are never deleted and never edited out of history: when an approved chapter contradicts an existing row, that row's `Status` becomes `superseded` and its text is left intact, while the corrected fact enters as a new row immediately beside it, with its own `Established` provenance and its own ID. Deleting the refuted row would erase the fact that the change happened, and the change is exactly what a continuity pass needs to see. A book is allowed to revise itself; it is not allowed to pretend it never did.

## Handoff window

Path: `continuity/window/NN-slug.md` — the same number and slug as the chapter file it hands off. One file per APPROVED chapter, no file for a chapter still in `drafting` or `user_review`: the window describes what the book has settled, and prose the user has not accepted has settled nothing.

Each handoff is about 30 lines — a ceiling, not a target — and carries five blocks, in this order and under these names:

- `What happened` — 3–6 bullets, plot and argument only, enough for the drafter of the next chapter to know where the book stands.
- `New facts` — the IDs added to the index by this chapter. IDs, not restatements: the fact itself lives in the index and is read there.
- `Open threads` — what the chapter opened and did not pay, with the ID of the thread row.
- `Character states` — where each character on stage ends the chapter: knowledge, relationships, physical situation. The thing a drafter gets wrong most often is handing someone knowledge they have not yet earned.
- `Voice notes` — anything this chapter settled about how the book talks: a register that worked, a habit to keep, a tic to stop.

The rotation is the point of the file's existence. The window holds the last K approved chapters, where K is `continuity_window` in `meta.json` — default `3`, range 2–10, defined in `references/state.md` and not redefined here. When a chapter is approved, its handoff is written and the handoffs beyond the last K approved chapters are DELETED from disk. The deletion is not a loss: the facts they recorded are rows in the index, and the surviving handoffs are handoff context only. A window kept for the whole book would be a second manuscript, and dispatching it would cost exactly what dispatching the manuscript costs.

The lifecycle has three moments, and the difference between them matters:

- Phase 2 — the chapter cycle. The window moves forward one chapter at a time, exactly as above. When the last chapter of the cycle is approved, the window is FROZEN: file added, no file edited, no file deleted after that point. Frozen, not finished — it is the handoff state of the drafted book.
- Phase 3 — the sequential passes. Each sequential pass REBUILDS the window as the sliding window of the pass in progress: reading chapter NN, the handoff in effect is regenerated from the chapters (NN-K)..(NN-1) as they stand at that moment, so a continuity pass sees the book as it now is and not as it was in phase 2. `references/passes.md` owns this rule and the order in which the passes run.
- Imported manuscripts. Here the window has to be filled before any window could have advanced: the diagnostic sweep reconstructs the facts index from the manuscript and populates the window with the last K imported chapters — the tail of chapters 1..M — so that the first drafting dispatch after M starts with handoff context rather than an empty folder. The sweep itself is `references/reconstruction.md`.

## Update after each approved chapter

The trigger is a state transition, not a feeling: a chapter becomes `approved` in `meta.json`, and before that chapter can influence another page, the ledger catches up with it.

You dispatch the Continuity-checker, pasting its role file — `references/roles/continuity-checker.md` — into the prompt with the input paths, following the dispatch rule in `SKILL.md`; you never paraphrase the role and never hand it the whole book. Its inputs are exactly three:

- the approved chapter file, `manuscript/NN-slug.md`;
- the handoff files currently in `continuity/window/`;
- `continuity/facts-index.md`.

Its outputs are exactly three, all on disk when it returns:

- new and updated rows of `continuity/facts-index.md` — new facts appended, contradicted rows marked `superseded` with the new row beside them, nothing deleted;
- the new handoff `continuity/window/NN-slug.md`, in the five-block form above;
- the pruning: every handoff beyond the last K approved chapters deleted, keeping the folder at K files.

Nothing about that list is yours to do. Your write in this protocol is `meta.json` — the chapter status, and whatever the gate recording requires — and that is all: you do not author index rows, you do not draft the handoff, you do not improvise a fact from session memory. If the Continuity-checker returns something that contradicts the canon rather than the index, that is a contradiction and not a ledger update; it goes through the contradiction protocol of `references/passes.md` and waits for the user.

## Change discipline

The rule that governs every line of this file: you never mutate the index before a user decision. Rows enter the table from exactly two channels — an approved chapter, or a bible the user has validated at Gate 1 — and a correction suggested from anywhere else, including your own reading of the prose, is not an update. It is a contradiction: STOP, follow the contradiction protocol of `references/passes.md`, and put the question to the user. The index is the book's memory of what has been decided; a memory that edits itself is worth exactly nothing at the next dispatch.

The single declared exception, written here so it is never applied by analogy: the diagnostic sweep of an imported manuscript — `references/reconstruction.md` — POPULATES the index before Gate 1 with rows marked `PROVISIONAL` (the `Status` column reads `provisional`), because on a manuscript that already exists the index cannot stay empty until the bible is approved. A `PROVISIONAL` row is marked exactly that way and stays marked until the user validates the reconstructed bible at Gate 1; only then does it become `canon` or `superseded`. The exception is about who may fill the table first, never about who decides: the decision stays with the user, and no row leaves `PROVISIONAL` without Gate 1.
