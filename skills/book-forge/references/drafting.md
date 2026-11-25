# Drafting — phase 2, the chapter cycle

Phase `chapters` is where the book acquires prose. Everything before it planned the book; everything after it edits the book. Here, one chapter at a time, a drafter writes new pages against the canon and the user decides after reading them whether the book moves on. The gate is not a formality at the end of the phase — it is the phase's unit of work, and this file describes the loop it closes.

You orchestrate this phase; you do not write it. The prose comes from the Drafter role, dispatched with its role file, `references/roles/drafter.md`, pasted into the prompt together with the input paths for that specific chapter, following the dispatch rule in `SKILL.md`; never paraphrase the role into the prompt and never hand it the whole book. Your writes in this phase are `meta.json` and the messages you put in front of the user — nothing else.

The phase runs on the state machine of `references/state.md`, which owns the enums and the transition rules; this file uses them and never redefines them. Two invariants bound everything below: `drafting` and `user_review` are legal only in phase `chapters` (C7), and a chapter that is still `planned` when the manuscript leaves this phase is an invalid state. That is the machine's way of saying what the human gate means: a chapter is either written and accepted, or the phase has not finished.

## The chapter cycle

One chapter, from the outline to the approved manuscript file, moves through exactly this sequence:

1. Pick the next chapter whose `status` is `planned`, in `outline.md` order, and write `status: drafting` for it in `meta.json.chapters`. Nothing is drafted before the chapter is in this state: the state file is what a resumed session reads, and a chapter written but not registered is work the next session cannot see.
2. Dispatch the Drafter, one chapter per dispatch, with the inputs listed under `## Dispatching the drafter`.
3. When the Drafter returns the chapter file, write `status: user_review` and present the chapter to the user. Nothing else is drafted while the chapter sits in this state — the pipeline is stopped at the gate, not slowed down by it.
4. The user reads. If they have corrections, they go back to the drafter and the chapter returns to `status: drafting` for the rewrite, exactly as `## User review and immediate rewrite` describes.
5. The user reads the rewritten chapter. This repeats as many times as the user wants, and the chapter never leaves the loop by any route other than approval.
6. The user approves. You write `status: approved`, and the closing protocol of `## Closing a chapter` runs before the next chapter is picked.

The chapter closes ONLY on approval: `status: approved` is the one transition out of the loop, and there is no partial state called "good enough to continue from". Silence is not approval, a chapter the user has not read is not approval, and a chapter the user read but did not comment on is approval only when they say so. When you are unsure whether the user approved, the answer is that they have not — ask, and leave the status where it is.

The active set is one chapter, or one block under `## Blocks of N`: the chapter (or block) that is in `drafting` or `user_review` is the only thing being written. Chapters after it stay `planned` until the pipeline actually reaches them.

For `work_mode: complete`, the cycle applies to the new chapters M+1..N only. The imported chapters 1..M are already `imported` and never re-enter drafting; they were stabilized before this phase opened, exactly as `references/reconstruction.md` records.

## Dispatching the drafter

The dispatch carries paths and a task, never content. Into the prompt go:

- the role file, `references/roles/drafter.md`;
- `bible.md` in full — it is the canon, and a chapter written against a summary of the canon is a chapter with canon failures baked into its prose;
- the chapter's own contract from `outline.md`: the section `## NN — <title>` with its Purpose, Contract, Beats, Continuity hooks and Target range;
- the handoff window, `continuity/window/` — the K most recent approved handoffs, K = `continuity_window` in `meta.json`. Pass the folder as it stands; the pruning rule belongs to `references/ledger.md` and you do not curate the tail by hand;
- the rows of `continuity/facts-index.md` that the chapter's Continuity hooks cite, and only those. Copy the rows into the prompt with their IDs and provenance rather than handing over the index: a drafted chapter needs the facts it depends on, and the index of a finished book is long enough to crowd out the contract it is meant to support.

What never enters the prompt: any other chapter of the manuscript, whole or excerpted, and the prose of earlier chapters in any form. The window exists precisely so this dispatch does not need them, and a drafter handed chapter 07 will imitate it instead of writing chapter 08. The chapter file being revised for the second time — its own current draft — is the single exception, and it is not another chapter.

The dispatch also states two things the files do not: the output file, `manuscript/NN-slug.md`, with `NN` zero-padded and the slug from `meta.json.chapters[].file` (the naming rules are `references/state.md`'s); and the language, `project.language`. The Target range comes from the chapter's contract, which took it from the heuristic of `references/bible.md` — a drafter given no range overshoots, and one given a range invented at dispatch time has been given a decision it was never allowed to make.

One chapter per dispatch. A prompt that asks for "the next three chapters while you are at it" produces a block of prose written from a single read of the window, which is the exact failure the gate per chapter exists to catch.

## User review and immediate rewrite

Presenting is yours, and it is a presentation, not a defence. Tell the user which chapter it is and that it is ready to read; do not summarise it in place of their reading it, do not pre-empt corrections by flagging what you would change, and do not offer your own verdict on the prose. The user reads the file.

Corrections travel to `the same drafter` VERBATIM. You copy what the user said — their words, not your interpretation of them, not a cleaned-up version — into the rewrite dispatch. Interpretation is where corrections quietly become your edits: "make her colder here" is a decision about the character, and it is the user's decision to phrase. If a correction is genuinely ambiguous, ask the user what they meant; never resolve the ambiguity on their behalf and never pass a guess to the drafter labelled as their instruction.

The rewrite is immediate. The corrections go out in the next dispatch, the drafter rewrites the chapter, and the chapter comes back for a new read. They do not accumulate to the end of the work, they do not wait for the next chapter, and they do not become a list "to handle in phase 3": a correction deferred is a correction made against a book that has already been built on top of it. This is the one place the pipeline deliberately spends round-trips — the drafter is fast, the user's reading time is not, and a wrong paragraph caught now costs one rewrite instead of a cascade.

You orchestrate; you never amend prose. You do not fix a typo the user mentioned, do not soften a sentence, do not apply "obvious" corrections the user did not ask for. The reason is not ceremony: the chapter has one author, and a second hand on the prose makes every later correction a negotiation between two voices the user cannot tell apart.

On a `stateless` harness — one-shot subagents with no memory of the previous dispatch — `the same drafter` cannot mean the same instance, and it does not have to. Re-dispatch the Drafter role with the chapter's current draft, the user's corrections verbatim, `bible.md`, the chapter contract and the window: the continuity of the chapter lives in the project files, not in the identity of the instance that wrote them. What must never happen is a fresh drafter handed a blank page and a correction — that is a rewrite of the chapter, not a revision of it. Name the harness limit in the dispatch only when it changes what the drafter is given; otherwise treat both cases as one rule: the same role, on the same draft, holding the same corrections.

After the rewrite the chapter goes back to `user_review` and the user reads it again. The loop exits at approval, never at "the corrections are in".

## Closing a chapter

Approval is a state transition plus a dispatch, in that order.

You write `status: approved` for the chapter, and then — before that chapter can influence the next one — you dispatch the Continuity-checker pasting `references/roles/continuity-checker.md`, so the ledger catches up with the prose: new facts and threads appended to `continuity/facts-index.md`, contradicted rows marked `superseded`, the chapter's handoff written into `continuity/window/`, the window pruned to the last K approved chapters. That protocol is `references/ledger.md`'s, cited here and never restated, and its writes are the Continuity-checker's alone — your writes stay in `meta.json`.

Then, and only then, the pipeline advances `only after the user approves the current chapter`: the next chapter is picked, or the phase closes. Drafting past an unapproved chapter is not a shortcut that saves a round-trip; it is prose written against a book that has not been agreed to, and the corrections it will need are corrections to chapters that already exist.

Two states need saying out loud at the end of a session. A chapter left in `status: drafting` or `status: user_review` is a chapter the next session will find and must not mistake for finished work; say which chapter is waiting, and on what. And when the manuscript's last planned chapter becomes `approved`, the phase closes: the orchestrator sets `phase: "passes"` and initializes `pass_scope` and `pass_progress` according to C6 of `references/state.md` — for `create` and `complete` all five passes in macro→micro order, `structure → continuity → style → grammar → spelling`, with `pass_progress` carrying exactly the same keys, each `pending`; for `revise` and `restyle` the scope fixed at Gate 1, listed here for completeness only, because neither mode drafts chapters and neither reaches this point through phase 2. Both modes have their own entry into `passes`, and a scope invented at a chapter gate would be a decision taken by the wrong phase.

Nothing else moves on approval. The bible is untouched by a drafting phase — when a chapter needed something the canon does not say, that is a question for the user, handled as `## Never` states and not settled by editing canon.

## Blocks of N

When `validation_mode.type` is `"blocks"` with `validation_mode.block_size` = N (N ≥ 2, recorded at intake and owned by `references/intake.md` and `references/state.md`), the gate falls after every N chapters instead of after each one. The drafting does not change; the rhythm of review does — and so does the way continuity travels inside the block.

- Draft N chapters of the block in outline order, one dispatch each, exactly as `## Dispatching the drafter` describes, with the same `status: drafting` → `status: user_review` per chapter. The difference at `user_review` is that you do not present yet: you pick the next chapter of the block.
- Inside the block, continuity travels as running context. Every dispatch after the first receives the earlier block chapters' Drafter ledger-notes — the new facts, threads, character states and voice decisions that note records — pasted into its prompt, because that is the only description of prose the user has not seen yet. The window is not touched and the index is not touched: `references/ledger.md` writes a handoff only for an APPROVED chapter and never mutates the facts index before a user decision, and a block chapter is `user_review` until the block is approved. Chapters drafted on running notes rather than on handoffs are exactly the extra risk the block mode buys the user out of, in exchange for fewer interruptions; say so if a block starts drifting.
- When all N chapters are drafted, present the block: ONE review session, the N chapters together, in order. One session, not one per chapter — a block the user opens N times is the per-chapter gate wearing a costume.
- Corrections come back per chapter and go out per chapter, verbatim, to the same drafter, immediately, exactly as `## User review and immediate rewrite` states: a correction to the third chapter of the block does not wait for a comment on the fourth. One correction round covers the whole block, and the chapters the user approved silently in that round stay as they are. Silence is not approval here either.
- When the user approves the block, write `status: approved` for every chapter of the block, then dispatch the Continuity-checker for each one IN CHAPTER ORDER, exactly as `## Closing a chapter` describes — each chapter gets its consolidated handoff, at block approval, and its rows, and the window pruned to the last K approved chapters. At that point the chapters are approved, so every write the ledger protocol forbids during the block becomes legal, in the order the book reads.
- NEVER write beyond the block awaiting review. The next block starts only when the current one is approved; a draft of chapter N+1 written while the user is reading 1..N is prose built on chapters that may still change, and it is the gate skipped in the name of momentum.

The block size is fixed by `meta.json` and is not renegotiated per block. A block short of N chapters at the end of the manuscript is legal: the last block is `min(N, chapters remaining)` and is reviewed as the block it is. Changing `block_size` mid-book is a user decision recorded in the state file, never an adjustment made because a chapter ran long.

## Never

- Never draft past the gate: no chapter beyond the one (or the block) awaiting review, no "just a first pass" on the next one.
- Never advance a chapter's status without the user's explicit approval — silence, a partial read, or your own satisfaction are not approval.
- Never update `bible.md` during drafting. A deviation the chapter needs is a question for the user, not a silent amendment to canon — the canon changes at Gate 1 or by an explicit user decision, never to make a draft legal.
- Never let a session end with a chapter in `status: drafting` or `status: user_review` and not say so: name the chapter, its state, and what it is waiting for.
