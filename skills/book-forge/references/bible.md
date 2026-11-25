This file is the creation track. If `work_mode` is not `create`, do not use it alone: with no chapters yet read `references/ingest.md`; with imported chapters read `references/reconstruction.md`.

# Bible and outline — phase 1, the canon of a book that does not exist yet

Phase `bible` is where the book stops being an intention and becomes a contract. Two artefacts leave this phase and both are judged at Gate 1: `bible.md`, the canon — what is true about this book and stays true until the user changes it — and `outline.md`, the plan — one entry per chapter, saying what each chapter is for and what it promises.

The distinction governs this whole file. `bible.md` is the book's contract, never a draft: nothing in it is manuscript prose, so no scene, no dialogue and no sample chapter has any business there. A bible that starts to sound like the book is a first draft hiding where no editor will look for it. The prose the user reads as prose arrives in phase `chapters`, written by a drafter against this canon; the bible decides what is true and the prose decides how it sounds.

The bible is also the file every later dispatch reads. A fact that lands there is binding on every chapter that follows, and a chapter that contradicts it is a canon failure, not a local liberty — which is why this phase ends on an explicit user approval and never on a draft that merely looks finished.

## Who works and how

You orchestrate; you do not write the canon yourself. The draft of `bible.md` and `outline.md` comes from the Researcher role — dispatch it with its role file, `references/roles/researcher.md`, pasted into the prompt together with the input paths for this task, following the dispatch rule in `SKILL.md`; never paraphrase the role into the prompt and never hand it the whole book.

Its inputs are exactly two things:

- The interview transcription — the answers to the core questions and to the profile topics from `references/intake.md`. The audience, central promise and tone/voice answers have no key in `meta.json`; this file is where they get a durable home, at the top of the profile template.
- `research/` — whatever raw material the intake interview copied there, unedited, plus `research/sources.md` when the book has external sources. Paths are passed, not pasted content: the Researcher opens the files it needs, and a folder of notes never travels through a prompt.

The Researcher returns drafts of both artefacts, written in the book's language (`project.language`), filling the profile template below field by field. A result that comes back as flowing prose instead of fields has misread the role: a bible is a structured contract, and a field the user can see and correct is worth more than a paragraph that sounds authoritative.

Nothing unvalidated becomes canon before Gate 1. What the Researcher returns is a proposal, and so is what you put in front of the user: until the approval recorded in `## Gate 1 — approve the bible`, a filled-in bible is a working document with no authority over any chapter. Keeping that distinction honest is your job, not the user's — never describe a draft as "the bible" in a way that suggests it is already settled.

`meta.json` stays yours alone. The Researcher never writes it and neither does anything else dispatched from here; you record the gate (rule 1 of `references/state.md`). Additional research — asked for by the user, or needed because the draft exposes a hole — loops back to the Researcher with the open questions, and back to you when the revised draft is ready to present again.

Which template applies is already decided: `genre_profile` in `meta.json` picks one of the three below, and all three carry the same mandatory style guide.

## bible.md — fiction template

Fields marked `[min]` are mandatory — a fiction bible missing one is not ready for Gate 1. Fields marked `[opt]` are filled when the material exists; leaving one empty is legal and honest, inventing content for it is not.

- `[min] Premise` — one sentence, in the shape "someone wants something and something stands in the way", followed by one paragraph saying what the book is: the promise a reader takes from the back cover, not the plot summary.
- `[min] Audience` — who the book is for, carried from the intake answer, concretely: age, situation, what they already read. It decides how much world is explained and how fast the opening chapter may move.
- `[min] Characters` — for each major character: name, want (what they pursue), need (what they actually require, which the story must force on them), arc (from which belief to which belief), and state at the start of chapter 1.
- `[min] World` — the places the book actually uses and the rules that hold in them: what is physically possible, what is socially permitted, what costs what. Include only what a chapter might have to obey.
- `[min] POV` — first or third person, one viewpoint or several, and which character carries each. If there are several, name who knows what: the whole point of the field is to stop a drafter from handing a character knowledge they cannot have.
- `[min] Tone` — the emotional register the prose aims at, in a few words the drafter can hold: dry and unsentimental, warm, claustrophobic, comic. It is not the style guide; it is the target the style guide serves.
- `[opt] Secondary arcs` — the subplots and the characters who carry them, one line each, with what they resolve.
- `[opt] Timeline` — the in-story chronology when the book does not run straight: what happens when, and where the narration begins relative to it.
- `[opt] Genre conventions` — the pay-off the reader expects from this genre, named so the outline can promise it and the chapters can deliver or deliberately withhold it.

## bible.md — practical nonfiction template

Same markers: `[min]` mandatory before Gate 1, `[opt]` only when the material exists. A manual's canon is a transformation, so the fields are ordered by it.

- `[min] Transformation` — from what to what, in the reader's terms: "starts unable to X and afraid of Y, ends able to X on their own". A manual without this field becomes a list of tips.
- `[min] Audience` — who is being transformed, with what they already know and own. It sets the depth of every explanation and what never needs explaining again.
- `[min] Core concepts` — the list of ideas the book teaches, one line each, with the term the book will use for each. One concept, one name, for the whole book: the synonym that creeps in at chapter 7 is how a manual contradicts itself.
- `[min] Reader promises` — what the reader can do at the end of each part, stated as a capability and not as a topic. These are the yardstick the outline is checked against at Gate 1.
- `[min] TOC logic` — the order the book advances in, and why that order and not another: dependency, increasing difficulty, a project built up step by step. The outline must follow it.
- `[opt] Prerequisites` — what the reader must bring, including tools and prior knowledge, so the book can neither condescend nor jump.
- `[opt] Domain glossary` — the terms of art the book uses, with a definition each, kept separate from the core concepts: a glossary explains, a core concept teaches.
- `[opt] Case studies available` — the real examples the user has and may reuse, each with a line on where it fits. Real material beats invented examples every time.

## bible.md — narrative nonfiction template

Same markers again. Here the canon is what actually happened, so the first field is a factual spine and not a plot.

- `[min] True spine` — the timeline of what happened, in order, with the parts the user witnessed marked as witnessed and the parts that came from elsewhere marked as reported. The telling may rearrange it; the events themselves do not move.
- `[min] Audience` — who the book is for and what they bring to it: prior knowledge of the events, proximity to the people involved, or none at all. It decides how much context the opening has to carry.
- `[min] Cast` — the real people who appear, under the name the book will use for each (their own, a changed name, initials), with their role in the events. Names are a factual decision and are fixed here, once.
- `[min] Theme` — what the book is about underneath the events: why this story, why now, what the reader should carry away.
- `[min] Sensitivities` — the privacy and consent constraints as hard rules: who must be protected, what may not be told, what must be told a certain way. The intake question about protecting people produces this field, and it binds every chapter without exception.
- `[opt] Narrative texture conceded` — how much reconstructed scene, dialogue and interiority the user authorises against bare reportage, and where. Heavy scene-writing over thin recollection manufactures facts that did not happen; the field exists to make the permitted amount explicit before a drafter guesses.
- `[opt] Sources` — the documents, interviews and pages the book relies on, with what each supports. Anything that ends up quoted needs a line in `research/sources.md` as well.

## Style guide

`## Style guide` is a mandatory section of `bible.md` in all three profiles, and a bible that reaches Gate 1 without it is incomplete: it is the one part of the canon that governs every sentence the book will ever contain.

It is normative. It says how this book must sound, in rules a drafter can follow and a reviewer can check, not how some chapter happened to sound on the day it was written. Cover, at minimum:

- Register and stance — who is speaking to the reader (a peer, a teacher, a coach, a narrator out of sight) and how close: warm or dry, plain or literary, encouraging or terse.
- Person and tense — first or third, past or present, and whether that applies to narration, to examples, or to both.
- Rhythm — a sentence-length rule the prose can be measured against: short by default, or long with short beats at the turns. One measurable instruction beats three adjectives.
- Lexical taboos — the words and constructions the book never uses, including the user's content taboos from the intake interview. A taboo list is more useful than a list of virtues.
- Few-shot examples — two or three short passages that sound right, and one that sounds deliberately wrong with a one-line reason why. Four lines of example teach a voice faster than a page of description.

This is the prescriptive guide, written before the prose exists. The other kind — the descriptive one, reconstructed from what a manuscript already does — belongs to `references/reconstruction.md`; that guide is derived from existing prose, and describing here what you have not prescribed is how the two get confused.

## outline.md format

`outline.md` sits at the project root and holds one section per chapter, in book order. Each chapter is a level-2 heading in exactly this shape:

`## 01 — <title>`

Two digits, zero-padded, then an em dash, then the chapter title. The number is the chapter's identity: it is the same number that `meta.json` records in `chapters[].number` at Gate 1 and the same one the manuscript file carries in `manuscript/NN-slug.md` (the naming rules live in `references/state.md` and are the authority if they ever disagree with this paragraph).

Under each heading, five blocks in this order, each named so the user can read them at a glance:

- Purpose — why the chapter exists in this book, in one or two sentences: what the book loses if the chapter is cut. A chapter that survives the cut test on purpose alone is not padding.
- Contract — what the chapter promises the reader, and what it resolves or answers. Written so that after reading the chapter one can say yes or no to it.
- Beats — fiction: three to seven beats, one line each, in order, each a turn and not a topic. Practical nonfiction: the key points the chapter teaches, plus the exercise or worked example where the chapter has one. Narrative nonfiction: the real events the chapter covers and the narrative texture it is allowed to use.
- Continuity hooks — the facts, characters or promises from earlier chapters this chapter depends on, stated as facts ("Marta already knows about the debt") rather than as pointers ("see chapter 3"). These hooks are the raw material the facts index is built from, so a fact stated here is one the project can trace later.
- Target range — the chapter's word range, taken from the heuristic below and adjusted once against the book's own target.

The count of sections is the book's chapter count, N: it is this list that becomes the chapter list of the project at Gate 1, so a chapter in the outline is a chapter the pipeline will expect. The order follows the profile template — fiction by escalation and turns, practical nonfiction by the dependency of the transformation, narrative nonfiction by the real chronology or by a deliberate reordering the outline names.

## Chapter length heuristic

Defaults per profile, to start from rather than to obey:

| Profile | Chapter length (words) | Default book target (words) |
|---|---|---|
| fiction | 2,000–4,000 | 80,000–90,000 |
| practical_nonfiction | 3,000–5,000 | 40,000–60,000 |
| narrative_nonfiction | 2,500–4,500 | 55,000–75,000 |

Derivation: chapters ≈ `length_target.words` ÷ the centre of the chapter range, rounded to a sensible whole (a 50,000-word manual at a 4,000-word centre gives 12.5, so twelve or thirteen chapters), and each chapter's Target range in the outline then comes from the profile's row. When the user states a target, that number wins and is recorded in `length_target` (`references/state.md` owns the field); these defaults exist for the many users who arrive with no word count at all, and they are modified by the user, never adjusted silently by you.

The introduction of a handbook is typically shorter than its chapters, 1,500–2,500 words: it carries no transformation of its own, only the promise of one. Say that out loud in the outline rather than stretching the first chapter to fit the row.

## Gate 1 — approve the bible

Present `bible.md` and `outline.md` to the user together — the bible first, because the outline is checked against it — in the user's language, with the `[opt]` fields left empty named as empty instead of quietly omitted. Say what they are approving: the canon that binds every chapter, and the chapter plan built on it. Then stop and let them read.

Corrections go back to the Researcher, the draft comes back to you, and the presentation happens again. What the user changes is the canon; what they approve is what the book will be held to.

The gate is explicit, and it is granted only by the user. Silence is not approval, a friendly "sounds fine" after no reading is not approval, and a draft that merely looks complete is not approval. Never auto-approve, and never set the gate to keep the pipeline moving.

Only on explicit approval do two things happen, together, in the same write to `meta.json` — the file that is yours alone:

- `meta.json.chapters` is initialised from `outline.md`: one entry per chapter, 1..N, each with `number`, `file` (`manuscript/NN-slug.md`), `title`, `status: "planned"` and `origin: "written"`. This is the creation track: nothing was imported, so every chapter is a chapter still to be written, and `planned` is exactly the status C7 of `references/state.md` expects at this point. The list is initialised here, at approval, and nowhere earlier — a chapter list invented before the user agreed would describe a book nobody has approved.
- `gates.bible_approved: true` and `phase: "chapters"` are written. From that moment the bible is canon rather than proposal: every drafter dispatch carries it, and changing it is a user decision, not an editorial convenience.

Gate 1 is the same gate for a book that already exists, reached through `references/reconstruction.md` with a reconstructed bible and, on `revise`, a revision plan; this file owns the creation path only, and the state contract is unchanged either way — `phase` may not pass `bible` without `gates.bible_approved` (invariant C2 of `references/state.md`).

If the user wants more research instead of approval, the loop returns to the Researcher with their questions, and Gate 1 waits. No phase change, no chapter list, no drafting.
