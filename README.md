# book-forge

An Agent Skill, harness-agnostic, that writes or corrects an entire book — novel or nonfiction — from an idea or an existing draft to a finished, exportable manuscript. It runs on pi, on Claude Code, and anywhere a harness can load a `SKILL.md` and dispatch subagents.

## What it does

book-forge takes a person who has a book in their head and produces a finished manuscript on disk, chapter by chapter, with a human gate at every step. It starts with an interview (the bible, the outline, the voice), then writes one chapter at a time and stops for the user to read and approve each one, then runs the professional passes — structure, continuity, style/voice, grammar, spelling — and finally renders an EPUB 3 that Kindle Create accepts plus an optional .docx. It stops at export: no KDP upload, no cover, no marketing.

## The four jobs

- **create** — write a book from scratch: no manuscript exists yet, only the idea and the answers to the interview.
- **complete** — finish a partial manuscript: the existing chapters are imported and stabilized, then the drafting continues from chapter M+1.
- **revise** — correct an existing book, even one written long before this skill existed: diagnose, rebuild the bible, agree a revision plan, then run the passes.
- **restyle** — give a finished book a new voice: the old book releases only canon, facts and ledger (never its style guide), a rewritten pilot chapter becomes the anchor, then style/voice runs first.

The job is self-revealed in the first conversation, never asked as a multiple choice before the agent knows what the user has; all four run the same underlying machine.

## How it works

The pipeline is a phase machine, and every phase has a reference file the agent reads before acting:

0. `intake` — the interview: work mode, genre profile, audience, promise, voice, language, target length, validation block size.
1. `bible` — the Researcher builds `bible.md` (canon, concepts or characters, style guide, glossary) and `outline.md`; an existing manuscript is ingested and reconstructed first. Gate 1: the user approves the bible before any prose.
2. `chapters` — the Drafter writes one chapter per dispatch against the outline contract; the user reads and approves each chapter (or each block of N) before the next one starts.
3. `passes` — the editor subagents run one pass at a time, macro to micro (a restyle opens on style/voice by design); each pass leaves a registry and a diff per chapter, and a contradiction stops the pass and asks the user.
4. `final_review` — a fresh Final-reviewer per chapter, in a new session, reports against the approved manuscript; the user approves.
5. `export` — `book.yaml` is composed from `meta.json` and pandoc renders `exports/<slug>.epub` (and optionally `.docx`).

A book project on disk looks like this:

```
<book-project>/
├── meta.json            # pipeline state — every phase, gate and chapter status
├── bible.md             # canon + style guide + glossary
├── outline.md           # table of contents + per-chapter contract
├── manuscript/          # 01-slug.md, 02-slug.md … one file per chapter
├── continuity/          # facts-index.md + window/ (the K most recent handoffs)
├── research/            # raw material, sources.md with URLs and access dates
├── passes/              # one registry per pass, contradiction files
├── reports/             # per-chapter and aggregate final-review reports
├── book.yaml            # export metadata
└── exports/             # <slug>.epub, <slug>.docx
```

All state lives in `meta.json`, never in the conversation: a project can be closed and resumed months later, in a different session, on a different machine, and the next action is read from the files on disk. The manuscript is plain markdown — one file per chapter, first line `# <title>` — readable and editable in any editor even if the skill and its harness are gone.

## Install — skills.sh

```bash
npx skills add <owner>/book-forge@book-forge
```

Replace `<owner>` with the GitHub owner of the published repository. The `@book-forge` part is the ref skills.sh resolves inside the repository; the Publishing checklist below verifies the command live before release and, if the CLI's default ref differs, the ref is aligned at publish time rather than kept as a guess.

## Install — pi

```bash
git clone https://github.com/<owner>/book-forge ~/.agents/skills/book-forge
```

pi ≥ 1.6.0 discovers skills recursively: every directory under `~/.agents/skills/` (the standard Agent Skills location) that contains a `SKILL.md` is loaded, so the clone target goes one level below the directory, named after the skill. Restart pi, or open a new session, and the skill is available.

## Install — Claude Code

```bash
git clone https://github.com/<owner>/book-forge /tmp/book-forge \
  && mkdir -p ~/.claude/skills \
  && cp -r /tmp/book-forge/skills/book-forge ~/.claude/skills/
```

Only the `skills/book-forge/` directory is the skill; the rest of the repository is development tooling. A symlink to that directory under `~/.claude/skills/` works the same way and keeps a fork in sync:

```bash
ln -s /tmp/book-forge/skills/book-forge ~/.claude/skills/book-forge
```

The repository name must stay `book-forge`: skills.sh indexes `<repo>/skills/<name>/SKILL.md`, and the directory name is the skill name every installer and every harness resolves.

## Requirements

Nothing is required for the core of the skill — the interview, the bible, the chapters, the passes and the final review run on the agent's own file tools and subagents, and no binary has to be installed for a book written from scratch.

`pandoc is optional`: it is needed only twice, for the .docx ingest (converting an existing manuscript from Word) and for the EPUB/DOCX export in phase 5. Without pandoc the manuscript is still a complete, valid book — one markdown file per chapter — and the skill says so instead of substituting a renderer that was never promised. pandoc is free software from pandoc.org, an installer on Windows and macOS and a package everywhere else.

.pdf ingest is the one format with an extra caveat: pandoc cannot read PDF, so ingesting a .pdf requires a dedicated text extractor on that machine; if none is available the skill declares the limitation and asks for another format (`.docx` or `.md`) rather than reconstructing from a lossy guess.

Node and Python are not runtime requirements: the `npx` one-liner above is run once at install time by Node's package runner, but the skill itself executes nothing except optional pandoc. `tests/` and `pyproject.toml` in this repository are development tooling for the repository, not part of the skill and never needed by an end user.

## Development

The checks are the contract; they run the same way locally and in CI.

```bash
git clone https://github.com/<owner>/book-forge
cd book-forge
uv run tests/check.py
```

Requirements for developing the repository: [uv](https://docs.astral.sh/uv/) ≥ 0.13 — Python itself is managed by uv and does not have to be installed. Plain `python` is never prescribed in this repository: on the machine these checks were built on, `python` resolves to the Microsoft Store stub, so every invocation goes through `uv run` (which also picks the interpreter from `uv.lock`).

What the checks freeze, so that a later edit cannot quietly break a contract the skill already promised:

- the `meta.json` JSON Schema and its invariants, exercised against the valid and invalid fixtures in `tests/fixtures/` — including the phase-gate coupling, the pass scope per work mode, and the chapter-status rules;
- the pinned headers and the pinned substrings of every reference file — the mechanical anchors for the design warnings W1–W5: the role path injected into every dispatch and the phase file re-read at every resume (W1), the ingest adapters — `.docx` through pandoc, `.pdf` through a dedicated extractor, and the user-confirmed chapter split (W2), the `skills/book-forge/` layout and the bounded frontmatter `description` (W3), the per-mode pass order, style/voice first in a restyle and the stabilization of chapters 1..M before chapter M+1 (W4), the fresh-subagent final review whose reports only the orchestrator aggregates plus the `facts-index.md` resync (W5);
- role-path and link integrity: every `references/roles/*.md` mentioned in `SKILL.md` must exist and be exactly the declared set, and no relative markdown link may dangle.

`.github/workflows/ci.yml` runs `uv sync --frozen` and then `uv run tests/check.py` on every push and pull request.

## Publishing checklist

Before the repository is announced:

1. Replace every `<owner>` placeholder in this README with the real GitHub owner.
2. Verify the install command live, from a clean machine: `npx skills add <owner>/book-forge@book-forge` must install the skill and make it loadable. If the CLI's default ref is not `@book-forge`, align the ref here and in this checklist to what actually worked — never ship an unverified command.
3. Tag the release — an annotated tag, `git tag -a v0.1.0 -m "book-forge v0.1.0"`, pushed to origin — so that a pinned install and a re-publish refer to the same tree.
4. Dogfood dry-run: run the skill end to end on a toy project (a 3-chapter book in `create` mode is enough) before publishing, to catch a broken dispatch path or a gate that does not close. Recommended, and deliberately outside the scope of the implementation plan.

---

Released under the [MIT License](LICENSE). Copyright (c) 2026 The book-forge authors.
