# Passes — phase 3, the correction engine

Phase `passes` is where the book stops acquiring prose and starts being corrected. The same engine serves all four work_modes: a drafting phase hands over a finished book; an imported manuscript enters here after its reconstruction; a restyle enters here after its approved pilot; and a completion enters twice — once for the stabilization of chapters 1..M in phase 1, once for the whole book in phase 3. What changes between them is the scope. What runs is the same five passes, in the same order, dispatched the same way.

This file owns the mechanics: the order of the passes and their scope per mode, how a pass is dispatched and what it may write, what happens when two chapters assert incompatible things, when the facts index is resynced, what a pass leaves on disk, and how the phase closes. It does not own the editors' routines — the role files of `references/roles/` say what each specialist looks for and when to stop — and it does not own the state machine: `references/state.md` defines `pass_scope`, `pass_progress`, the `stabilization` block and the invariants that bind them. The scopes below are the practical reading of invariant C6, not a second copy of it.

Two rules hold for every pass in this file. One chapter per context, always: no dispatch ever receives the manuscript, and the ledger is what carries the book from chapter to chapter. And no pass runs alongside another: a pass closes — registry aggregated, resync done where one is due — before the next one opens.

## Pass order and per-mode scope

The five passes run in a fixed order, `macro to micro`:

`structure → continuity → style/voice → grammar → spelling`

Why this direction and not the intuitive one (B1): every pass that rewrites prose runs before the micro corrections, so the prose that comes out of a rewrite is still checked downstream. Run spelling first and the style pass then rewrites the sentences it corrected — the corrections were validated against text that no longer exists, and nothing after them re-reads it. Macro to micro is not a taste for large edits; it is the only order in which the last pass is the one that leaves the text verified.

The arrow string is the human-facing name of the sequence. The keys in `meta.json` are `structure, continuity, style, grammar, spelling`, with `style` the key of the style/voice pass; `references/state.md` owns the enum and rule 7 states the per-mode contract this file applies.

- `create` and `complete` — all five passes, in the order above.
- `revise` — the subset the approved `revision-plan.md` selects, in the same macro-to-micro order, never empty. The plan is where the scope comes from and Gate 1 is where it is fixed (`references/reconstruction.md` owns that derivation); this file takes the scope as given and runs it. A pass the plan does not cover is not invented at run time, and a plan block whose pass is missing from `pass_scope` is a Gate 1 inconsistency to resolve with the user before the phase opens.
- `restyle` — exactly `style/voice → continuity → grammar → spelling`. No structure pass: the structure is not the problem, the voice is the job, and the approved `pilot.md` is the anchor every style dispatch carries (see `## How each pass runs`). Continuity runs after style because the rewrite can drift facts; grammar and spelling follow because the new prose needs the same downstream verification as any other (B1).
- `complete`, stabilization (phase 1) — only `structure` and `continuity`, over the imported chapters 1..M, before chapter M+1 is drafted. `references/reconstruction.md` says WHEN this run happens and in which bookkeeping order; this file says HOW the two passes run, which is exactly as described below. Stabilization is tracked in the `stabilization` block of `meta.json` and NEVER in `pass_scope` or `pass_progress`: those two fields are initialized at the entry into `passes`, where C6 binds `complete` to the full five-pass scope, and a two-pass stabilization is not that run.

`pass_progress` is the progress board: one key per pass in `pass_scope`, moved to `in_progress` when the pass opens and to `done` when its registry is aggregated and its resync, where one is due, is on disk. The phase ends when every key reads `done` — never earlier, and never by inference from the conversation.

## How each pass runs

The five passes come in two execution shapes, and the shape follows from what the pass has to compare.

`structure` and `continuity` run per chapter IN SEQUENCE. These are the passes that must know what the earlier chapters now say, and the only way to know it without loading them is the ledger, read one chapter at a time, in order. `one chapter per dispatch`: the chapter file, its contract from `outline.md`, the canon, and a compressed view of `continuity/facts-index.md` — the rows that bear on the chapter's entities, promises and threads, not the whole index and never the book. The structure editor returns a restructured chapter; the Continuity-checker returns a chapter reconciled with the facts, or a STOP file. Either way the dispatch's own writes are its chapter plus its per-chapter registry fragment; the index is the Continuity-checker's and its edits follow the resync rule of `## facts-index resync`.

AT THE START of each sequential pass, `continuity/window/` is REBUILT as the `sliding window` of the current pass. Reading chapter i, the handoff in effect is regenerated from chapters (i−K)…(i−1) as the text now stands — K is `continuity_window` in `meta.json`, and the five-block handoff form belongs to `references/ledger.md` — and for the first chapters of the book from as many handoffs as exist before i. The phase-2 window is frozen at the end of the chapter cycle and is never reused: a continuity pass reading phase-2 handoffs would be checking the book against a description of its earlier self. Two consequences are worth stating because both have been mistaken for edge cases. The rebuild is this file's rule, and the `sliding window` lifecycle in `references/ledger.md` cites it rather than restating it. And after the reconstruction sweep of an imported book the folder may hold up to M handoffs; the rebuild is what normalizes it to K. Pruning that tail is not a chore handed to the Continuity-checker at pass start — the rebuild simply produces the window the pass needs.

`style/voice`, `grammar` and `spelling` run per file and are PARALLELIZABLE: one chapter per subagent, fresh context, no chapter needing another to be corrected. What gives the style pass its coherence without reading the neighbours is the anchor, not the context. On `restyle` EVERY style dispatch includes `pilot.md` and the bible's `## Style guide` as few-shot evidence of the target voice (W4) — every dispatch, not only the first, because an anchor given to chapter 01 and dropped by chapter 04 is a different voice from chapter 04 onward.

The parallel passes write ONLY their own chapter file and their own per-chapter fragment, `passes/registry-<pass>/ch-NN.md`, NN being the number of the chapter the dispatch corrected. They never write the pass registry: `passes/registry-<pass>.md` is `aggregated by the orchestrator` at the end of the pass, in chapter order 01..NN. The separation is not tidiness. Twelve subagents appending to one file produce interleaved entries and a file whose order nobody decided; fragments produce one local piece of evidence per dispatch, and the aggregation produces the linear record the gate reads. No concurrent write ever touches the pass registry, and that is exactly what makes it usable as Gate (b)'s evidence.

Every dispatch, in both shapes, carries the role file — `references/roles/structure-editor.md`, `references/roles/continuity-checker.md`, and `references/roles/copy-editor.md` one pass at a time — pasted into the prompt with the input paths and the prescribed output channel, following the dispatch rule of `SKILL.md`. Never the whole book, and never the manuscript as a folder: a subagent handed `manuscript/` will read it.

## Contradiction protocol

The Continuity-checker compares each chapter against the index, and this protocol is what happens when the comparison cannot be settled inside the pass (B2). A contradiction is not a doubt: it is two statements on disk, each with its provenance — `[ch.04]` says X, `[ch.12]` says Y — and a book that asserts both. A suspicion with one provenance is a question for the user, not a contradiction. The rule that nothing mutates before a user decision belongs to `references/ledger.md` and holds here without exception.

The protocol forks on one test: can the validated bible decide?

If it can, and univocally, the fix is automatic and `only the chapters in error` are touched. The conflict can sit on a later chapter — chapter 12 broke a canon that chapter 04 established — or on an earlier one — chapter 04 was already wrong and chapter 12 is the first place the book noticed. An earlier chapter gets a targeted dispatch on that chapter, always `one chapter per dispatch`: the pass does not adjust chapter 12 so that it agrees with the mistake, and it does not rewrite a run of chapters because one of them was wrong. Three writes follow the fix: the corrected chapter, the corrected index rows (the refuted row marked `superseded` with the corrected row beside it, append-only, exactly as `references/ledger.md` requires), and a registry entry that records both provenances. A fix that would need more than the chapters in error is not an auto-fix with a wide blast radius; it is a canon question in disguise, and it goes to the second branch.

If the canon cannot decide, `stop and ask the user`. The Continuity-checker writes `passes/contradiction-NN.md` — NN two digits, sequential, never renumbered — carrying both versions, both provenances and the decision schema: what the user is choosing between, and what each choice changes in the book and in the index. The pass on that file HALTS at that chapter: no later chapter of that pass is dispatched while the question is open. The ledger does NOT mutate: no `superseded`, no new row, no provisional guess as a placeholder, because an index that guesses is an index the next dispatch will believe. The user's decision updates `bible.md` and the index and unblocks the pass at the chapter where it stopped.

The guard is absolute and belongs to the phase rather than to the pass: NO micro pass — `style/voice`, `grammar`, `spelling` — starts while an open `passes/contradiction-*.md` exists. A STOP file is open until the decision is recorded and the artefacts it changed are resynced. The reason is B1 once more: a micro pass polishes sentences, and a contradiction can delete the sentence being polished. Correcting the typography of a book whose canon is still undecided is work done on a text that is about to change.

## facts-index resync

The index is the book's memory, and phase 3 moves the text that memory describes (W5). Two moments force a resync, and a third closes the phase.

One: after the `structure` pass closes. That pass has moved, merged, cut or reordered material, and a row reading `[ch.07]` may now point at a chapter that no longer establishes it. Two: after every canon-changing auto-fix of `## Contradiction protocol`, on the rows the fix touched. In both cases the Continuity-checker is dispatched with the task `resync facts-index` on the chapters touched, BEFORE the next pass starts: rows updated with their new provenance, statuses corrected where the fix refuted a fact. A resync deferred to "when the passes are over" is an index that migrates from pass to pass carrying provenance nobody can trust.

The third moment is the end: while the gate is being prepared — after the last pass, before the registries go in front of the user — the final resync runs on whatever the last passes touched. Rule 8 of `references/state.md` names the same dispatch in the controlled rollback from `final_review`, which is why the task has one name and one shape wherever it appears.

What a resync is, said plainly because the boundary is easy to cross: it is MAINTENANCE of existing rows — provenance `[ch.NN]` updated to where the fact now lives, status corrected where the fix settled it — on facts the index has ALREADY admitted. It is not a third admission channel. The two channels of `references/ledger.md` remain the only two: an approved chapter, and a bible the user validated at Gate 1. A resync that finds a statement in the prose with no row to maintain does not mint the row; that is a contradiction or a Gate 1 question, and it goes back through `## Contradiction protocol` to the user who owns it.

## Diff registries

Every pass leaves exactly one registry, named after its pass key: `passes/registry-structure.md`, `passes/registry-continuity.md`, `passes/registry-style.md`, `passes/registry-grammar.md`, `passes/registry-spelling.md`. One file per pass, with no merged registry and no ad-hoc names: the gate reads them pass by pass, and the final review cites them chapter by chapter.

The entry is per chapter, and it is built from the dispatch's own fragment, `passes/registry-<pass>/ch-NN.md`:

- date — the day the pass ran;
- chapter and file — `ch.07`, `manuscript/07-slug.md`;
- issues found — type and count: the classes of problem the pass was looking for, and how many of each it found;
- changed — yes or no, with the count of changed passages when yes;
- summary per intervention class — one line per kind of fix, with how many;
- ONE before→after sample — a short quoted pair, the concrete evidence a reader can judge;
- contradiction pointer — when the chapter raised or was touched by a `passes/contradiction-NN.md`, its path and its state.

A "changed: no" entry is a result, not an omission: it is the pass saying it looked and found nothing. A registry where every chapter changed is a registry that found a different problem than the one it was dispatched for, and it should be read with that suspicion.

In `work_mode: complete` the registries of `structure` and `continuity` carry two sections: `stabilization (phase 1)` for the run over chapters 1..M before drafting opened, and a phase-3 section for the run over the whole book afterwards. Two runs of the same pass, one file: that heading is what lets the user tell which fixes the imported half received before it was extended and which came later.

The registry is evidence of the diff (objective 7), not a diary of the work: it exists so a reader can verify what changed without re-reading the book, and so the gate described below has something to sample. Nothing goes into it that did not happen, and nothing that happened is left out of it.

## Gate — protocol (b)

Phase 3 ends in front of the user, with the registries as the evidence (user decision 9). Everything the passes did is on disk before the user is asked anything: the per-pass registries in macro-to-micro order, with counts and samples, and the final resync already run. The gate is a reading, not a conversation.

The orchestrator offers SAMPLING: the user names chapters — the ones whose entries are heaviest, the ones a contradiction touched, the ones they are simply curious about — and re-reads those. Sampling is an offer and is presented as one: what the registries say, what was repaired where, and which chapters would be worth a second look.

The FULL re-read is ALWAYS available: when the user wants to reread everything, they reread everything. It is not a privilege earned by a long diff, not conditioned on a reason, and not negotiated down to "the chapters that matter". A gate that offers only the sampler is a gate that asks the user to approve a book they have not seen.

The gate closes ONLY on explicit approval. At that point, in one write to `meta.json`, `gates.passes_approved: true` and `phase: "final_review"` — rule 2 of `references/state.md`, invariant C2. Silence is not approval, a sampled read is not approval of the unsampled chapters, and the orchestrator's own satisfaction counts for nothing. Three conditions hold before the gate is presented: no open `passes/contradiction-*.md`, every pass in `pass_scope` at `done` in `pass_progress`, and the final resync on disk. A gate presented over an unresolved contradiction asks the user to approve a book that contradicts itself.

A rejection is a decision too. The passes it names reopen as targeted runs on the chapters it names, with their fragments appended to the existing registries, and the gate is prepared and presented again. Nothing moves out of this gate except on approval.
