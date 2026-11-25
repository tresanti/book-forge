# Intake — phase 0, the entry interview

You run phase 0 inline, in the main conversation, because it is a conversation with a person: there is no project on disk yet, so there is nothing to delegate. Read `references/state.md` before you write anything down — it owns the `meta.json` contract that this interview feeds.
This file is the question bank: it decides which questions you ask, in what order, and what you record at the end. As an artifact it is English and stays English; the conversation does not — you phrase every question in the user's own language as you ask it, and the answers come back in that language too.
The interview is finished when you hold the values the pipeline needs: the job (work_mode), the genre profile, the audience, the central promise, tone and voice, the book's language, the target length, and the validation mode.

## Protocol

Ask one question at a time and wait for the answer before asking the next: a wall of questions is where a non-writer abandons the project, and it also denies you the chance to follow up on what was just said.
Ask in the user's own language, detected from the conversation so far; only the enum values and the file names you record stay English. The pinned rule from `SKILL.md` applies unchanged here: one question at a time.
No editorial jargon without explaining it in plain words the first time you use it — "beta reader", "POV", "arc", "style guide" all need a half-sentence of translation. When in doubt, ask the plain question and name the term afterwards.
Never ask what you can already infer. If the user volunteered "I've got eleven chapters in Word and I hate the ending", you do not ask whether a manuscript exists; you confirm the inference and move on.
Record each answer as you receive it, in your own notes for the session; the durable record is written once, at the end, in `meta.json`.
Keep the interview short. Twenty questions is the ceiling for a book that does not exist yet, and far fewer when the user arrives with material.

## Step 1 — identify the job

The job is auto-revealed, never chosen from a menu in the abstract: the user does not know this skill has four modes, and asking "which mode?" would force them to learn your vocabulary. Ask what exists instead, and let the answer pick the mode.

- Nothing written yet, only an idea or a rough intention → `create` (a new book from scratch: novel, handbook, narrative nonfiction).
- A partial manuscript with real chapters already in it, intended to be finished → `complete`.
- A finished book that needs fixing — including one written by hand, before this skill existed → `revise`.
- A finished book whose content is fine but whose voice must change → `restyle`.

If files arrive and the intent is not stated, ask one disambiguating question with the three existing-manuscript options in plain words: fix the writing as it stands, write it again in a different voice, or continue it from where it stops. Do not start converting or reading files before this answer: the mode decides which reference file opens next.
The recorded outcome is `work_mode`, exactly one of `create | complete | revise | restyle` — lowercase enum values, pinned by `references/meta.schema.json`, never paraphrased and never capitalised.

## Step 2 — validation mode (ask first)

This is the mandatory first question of the interview, before genre, before the title, before anything about the book: how much of it does the user want to read and approve at a time?
Two answers are legal, and both are about the human gate, not about drafting speed:

- One chapter at a time — the default. Record `validation_mode.type = "chapter"`; the pipeline stops after every single chapter and waits for approval.
- Blocks of N chapters — record `validation_mode.type = "blocks"` plus `validation_mode.block_size = N`, with N an integer of at least 2. The gate then falls after every N chapters instead of after each one; `block_size` is required in this case and meaningless in the other.

Ask it first because it sets the rhythm of the entire book's production and it is the one answer that silently changes every later gate. If the user has no opinion, default to `chapter` and say so out loud: it is the safer choice, and switching to blocks later is a user decision, not an agent's convenience.
No third value exists. Never invent an in-between like "every two or three chapters, we'll see": the enum is closed, and an unrecorded preference cannot be honoured later.

## Core questions (all profiles)

These are asked for every book, whatever the profile, after the validation mode:

- Genre profile — `genre_profile`, one of `fiction | practical_nonfiction | narrative_nonfiction`. Ask in the user's terms ("a novel?", "a manual?", "a true story told as a story?") and record the enum.
- Audience — who the book is for, as concretely as the user can say it (age, situation, what they already know). This drives the tone of the prose and the depth of the explanations.
- Central promise — the one thing the reader gets by the last page. One sentence in the user's words; it becomes the anchor of the bible and the test of every chapter.
- Tone and voice — how the book should sound (warm, dry, direct, literary, reassuring). Ask for a comparable book or writer only if the user offers one.
- Book language — `project.language` as a BCP-47 tag (`en`, `it`, `pt-BR`): the language the manuscript is written in, which is not necessarily the language of the conversation.
- Target length — `length_target`, with `words` and `chapters` (each may be null). Non-writers rarely think in word counts, so offer a comparison ("a short book of about eight chapters, or a long one?") and translate the answer yourself.

## Question topics — fiction

Open with the premise in one sentence: who wants what, and what stands in the way. If the user cannot compress it yet, that is a finding worth recording, not a failure — the bible phase will build it with them.
Then, in this order, and skipping whatever is already answered:

- Protagonist and desire — who the story follows, what they want at the start, and what they are wrong about.
- World and setting — where and when, and how much of it the reader needs explained.
- Point of view — first or third person, one viewpoint or several. Say what each choice costs in plain words before the user picks.
- Time span — how much in-story time the book covers, and whether it moves forward in a straight line or jumps.
- Emotional core — what the story is really about underneath the plot: what the user wants the reader to feel at the end.
- Ending — known from the start, or to be discovered while writing. Both are legitimate, but the drafting rhythm differs, so record the answer.
- Content taboos — anything the user refuses to write or refuses to read (violence, explicit sex, religion, real people). This becomes a standing constraint for every drafter.

## Question topics — practical nonfiction

Open with the reader's transformation: from what to what. "The reader starts here, unable to X, and ends there, able to X" is the shape to reach; a manual without it becomes a list of tips.
Then:

- Reader prerequisites — what they must already know or own (tools, software, prior knowledge). Stating this prevents both condescension and unexplained jumps.
- Promises per part — what each part of the book promises to deliver, so the outline can be checked against it at Gate 1.
- Exercises and examples — how many, of what kind, and whether the user has real cases to reuse. Real material from the user beats invented examples every time.
- Tone register — direct and terse, or empathic and encouraging; who is speaking (a peer, a teacher, a coach).
- Author's authority — the experience the book rests on, which the bible records as the ground for any claim you will later research or cite.

## Question topics — narrative nonfiction

Open with the real timeline: what actually happened, in what order, and which parts the user witnessed. Narrative nonfiction is built on facts that must survive the telling, so this timeline is the spine, not colour.
Then:

- Real people — who appears, under what name (their own, a changed name, initials), and which sensibilities or privacy limits apply. Ask explicitly whether anyone must be protected, and record it as a hard constraint on the canon.
- The theme — what the book is about under the surface of the events: why this story, why now, what the reader should carry away.
- Narrative texture — how much reconstructed scene, dialogue and interiority the user wants against bare reportage. The honest answer matters: heavy scene-writing over thin recollection creates facts that did not happen.
- Evidence on hand — documents, journals, recordings, correspondence the user already owns, which go to `research/` and shorten the rest of the interview.

## Raw material

Ask whether the user has material to hand: notes, files, a partial draft, scattered concepts, a folder of documents. Anything they provide is copied into `research/` of the project, unedited — it is input, never canon, and the bible is what turns it into canon.
When material exists, the interview starts from it: read what the user gave you and ask only about the gaps. Fewer questions, better answers.
Every external source that ends up used — an article, a book, a page consulted online — gets a line in `research/sources.md` with the URL and the access date, because a quotation without its source is forbidden by the skill's global rules, whichever phase produces it.
Never overwrite or reorganise the user's own files in place: copy, then work on the copy.

## Online research

Online research happens only when the user asks for it, never as an autonomous initiative during the interview. If they ask about web access, probe the environment once and record the outcome: `flags.web_available` becomes `true` or `false`.
`null` is legal only while `phase` is `intake` (invariant C4 in `references/state.md`): by the end of this phase the flag must carry a real boolean, so probe before you write `meta.json` — and never claim access you have not verified.
If the environment has no web access, say so immediately and plainly, and plan to work from the user's own material only. This is the protected exception in `SKILL.md`: a researcher without web access declares the limit up front and never silently fabricates sources or citations.

## Write meta.json

At the end of the interview you create the project, and you do it yourself: `meta.json` is written only by the orchestrator, never by a subagent — no role file may write it. Confirm `<project-dir>` with the user before creating anything (an existing folder to open, or a new one, named from the book title in kebab-case ASCII).
Create only the directories the pipeline will actually use — `manuscript/`, `continuity/`, `research/`, `passes/`, `reports/` — then write `meta.json` with the field set owned by `references/state.md`: `schema_version: 1`, `project{title, slug, language, created}`, `work_mode`, `genre_profile`, `validation_mode`, `phase: "bible"`, `flags{awaiting_fresh_session: false, degraded_non_independent: false, web_available}`, `gates` all false, `chapters: []`, `continuity_window: 3`, plus `length_target` when the user gave one. Validate it against `references/meta.schema.json` before moving on.
`chapters: []` is correct in every work_mode. On `create` the chapters are invented in the bible phase; on `complete`, `revise` and `restyle` they arrive from ingestion, and until the user has confirmed the chapter split the list stays empty — a legitimate state during phase `bible`, tolerated by invariant C8 up to Gate 1.
What happens next is decided by `work_mode`, following the routing table in `SKILL.md`: a `create` project continues in `references/bible.md`; work on an existing manuscript continues in `references/ingest.md`, which converts the files, proposes the split and hands over to `references/reconstruction.md` once the chapters are registered.
