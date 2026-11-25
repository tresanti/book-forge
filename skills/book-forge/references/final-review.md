# Final review — phase 4, the gate that reads the book one chapter at a time

Phase `final_review` opens on the approved registries of phase 3: `gates.passes_approved: true` and `phase: "final_review"`, written in one move by the gate protocol of `references/passes.md` (rule 2 of `references/state.md`, invariant C2). The book is finished being made. Nothing in this phase writes prose, moves a paragraph, or settles a fact: the phase produces a verification and then a decision.

The verification is a fresh, independent reading of the whole book, chapter by chapter, by readers who have never touched it — objective 9. Two constraints shape it and neither is negotiable. The gate must not be run by the context that wrote the book: whoever corrected a sentence believes the sentence is now correct, and a review performed by the author of the work is not a review. And no context may hold the book: a reviewer handed all N chapters reads them the way their writer did, by memory of the previous chapter, and the last chapter is judged by a context already full (B4, W5). So the gate is per-file verification with an aggregated report, and freshness is a property the pipeline has to arrange rather than assume.

This file owns the arranging: the fresh-session rule inline, the shape of the per-chapter dispatches, what the aggregation is and is not, the one rollback a rejection is allowed to trigger, and how the phase closes. It does not own the reviewer's routine — `references/roles/final-reviewer.md` says what one reviewer looks for and what it may write — and it does not own the state machine: rules 3 and 8 of `references/state.md` define `awaiting_fresh_session`, `degraded_non_independent` and invariant C3, and this file applies them.

## Fresh-session rule

The gate must run in a context that has not drafted or edited this book. That is the whole of the rule, and it is a fact about the context, not a promise about the intent: a session that has written or corrected prose in this project is not fresh for this project, no matter how carefully it now tries to read.

With subagents available, the orchestrator gets freshness for free — every per-chapter dispatch is a new context that has never seen the book — and the phase proceeds. Inline, with no subagent tool, the orchestrator has no way to open a context it is not already in, so the pipeline stops instead. At the end of phase 3, in the same write that closes Gate (b), it sets `awaiting_fresh_session: true` and stops HARD.

Stopping hard means exactly that: no review dispatch, no sampling, no "just the first chapter while the user is here", no partial report. The announcement to the user is one sentence and it is not negotiable — the book is ready for its final review, and the review runs in a new session; close this one and open a new one on the project. A session that starts reviewing anyway is a session reviewing its own work.

The NEW session recognises itself as fresh by the only test that exists: it has run no drafting or editing turn on this book in its own context. Reviewing earlier chapters does not disqualify it — reading is not writing — but drafting, rewriting and every pass that edits a file do. Having established that, it sets `awaiting_fresh_session: false` and starts the gate by reading ONLY `meta.json` and this file. Not a summary of the previous session, not a recollection of what was fixed in phase 3, not the manuscript in bulk: the disk is the state, and the per-chapter dispatches are what bring the prose in front of a reader.

With long books inline, the review dispatches are split across several consecutive fresh sessions. Chapters 1..k are reviewed in one session, k+1..N in the next, and the handover is a new context starting again from `meta.json` and this file: `one fresh subagent per chapter` is a rule about what one context may hold, and a review that has to carry twenty chapters of findings to reach the end of the book has broken it from the other side. What a session may never do is keep going while its own context is the bottleneck — the split is the mechanism, and the review does not shrink to fit.

A self-review is allowed only on an explicit user request, and it is recorded, not merely performed: `degraded_non_independent: true` in `meta.json` (rule 3), and the marking is the first line of the aggregate report. Silence is not the request, a user who is in a hurry is not the request, and the orchestrator's judgement that the last pass "barely changed anything" is not the request. The two flags are never both `true` — invariant C3 — because a review cannot be simultaneously waiting for a fresh session and running degraded inside the current one.

## Per-chapter dispatches

The gate dispatches the Final-reviewer `one fresh subagent per chapter` (W5). One chapter means one dispatch: the reviewer receives the chapter file, `bible.md`, the rows of `continuity/facts-index.md` that carry the chapter's provenance and entities, and the pass registries' entries for that chapter — the registries relevant to it, so the reviewer can test the claims the corrections made. Those inputs are the whole of the dispatch, following the dispatch rule of `SKILL.md`, with the role path `references/roles/final-reviewer.md` pasted into the prompt.

The dispatch carries never the manuscript as a folder, never a second chapter, and never a run of chapters to "get a sense of the book": a subagent handed `manuscript/` will read it, and a reviewer who has read chapter 06 while judging chapter 07 has started comparing the book to itself instead of to its canon.

The exclusion is part of the dispatch, not a matter of taste (O6). A chapter's reviewer is `never the chapter's own drafter` — never the agent that wrote or rewrote that chapter during the chapter cycle, in phase 2 — `nor its Phase 3 editor`, the pass specialist that touched it in phase 3. A chapter rewritten by the drafter and then corrected by the copy-editor has two agents in its history and neither may review it. The reason is the same as the fresh session's, one dispatch smaller: the reviewer must be outside the work being reviewed, and the structure editor who repositioned a scene has already decided the scene belongs where it is now. Where a role must be reused because no other agent exists, that is a degraded review, and it is recorded as one.

Each dispatch writes one file and returns: `reports/final-review/ch-NN.md`, NN the two-digit chapter number, the report whose format `references/roles/final-reviewer.md` fixes. The orchestrator collects the files; nothing else per chapter is produced, and no finding lives only in the dispatch's reply.

## Aggregate the reports

The orchestrator `aggregates the per-chapter reports only`. It does not re-read the chapters, does not sample them, and does not add a judgement of its own to the verdicts it is assembling — the book was read once, per chapter, by a fresh reader, and a second reading in the orchestrator's context would be the single-context review this phase exists to avoid.

The aggregate is `reports/final-review.md`, assembled from the per-chapter files in chapter order and carrying these headings, in this order:

- `Verdict per chapter` — one line per chapter, `ch.NN` and the verdict the reviewer returned, so the book's state is legible before any detail.
- `Unresolved markers` — every TODO, PLACEHOLDER, bracketed note or `[...]` reported, with the chapter that carries it.
- `Style violations` — the departures from the style guide, with the clause they depart from.
- `Continuity breaks` — the facts, entities, promises and threads found in conflict with the index or the canon, or missing where the book promised them.
- `Risk areas` — what the per-chapter reports flag as thin, over-explained, or needing a decision the reviewer could not make inside one chapter.

Every line carries its chapter, so the user can go from the aggregate to the per-chapter report and from there to the prose. The overall verdict closes the file: the book passes the final gate when every chapter does, and it does not pass by majority.

When a chapter does not pass, the gate does not close and the book does not advance. The rollback is the one planned in rule 8 of `references/state.md`, and it has a fixed order: explicit user confirmation → `phase: "passes"` with `gates.passes_approved: false` → a targeted pass on that chapter, the pass the finding names, plus `resync facts-index` → a new Gate (b) → a new entry into `final_review`. Nothing is edited at the final gate and nothing is approved around a failure: the correction happens in phase 3, with the pass registries recording it, and the book comes back to this phase to be read again. Inline, that re-entry sets `awaiting_fresh_session` back to `true`, because the session that ran the targeted pass has just edited prose and is no longer fresh for this book.

## User approval

The aggregate report goes to the user as the gate's evidence: verdict per chapter, unresolved markers, style violations, continuity breaks, risk areas, and the overall verdict. The user may open any per-chapter report, and any chapter of the manuscript — a full re-read is always available, and the aggregate is a map of where to look rather than a substitute for looking. What the orchestrator must not do is summarise the reviews in conversation as though the summary were the report: the file is the record, and it is what the approval is given on.

The gate closes ONLY on explicit approval. At that point, in one write to `meta.json`, `gates.final_approved: true` and `phase: "export"` — rule 2, invariant C2 — and phase 5 takes the book away from review and into export. Silence is not approval, a spot-check of two chapters is not approval of the other eighteen, and a book that failed a chapter and was never re-reviewed is not approved at all.

When the review ran degraded, the approval is given on a report that says so. `degraded_non_independent` is the first line of `reports/final-review.md`, and the user is told in the same breath that the gate they are approving was not independent: the marking is not a footnote for a future auditor, it is the fact the user needs in order to decide whether to approve. Everything else about the approval is unchanged — the gate is the user's, and it is still the last word on the book.
