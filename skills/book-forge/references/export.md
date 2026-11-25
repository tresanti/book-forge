# Export — phase 5, the approved book becomes files

Phase `export` opens on the last gate of `references/final-review.md`: `gates.final_approved: true` and `phase: "export"` written in one move, as rule 2 of `references/state.md` requires and invariant C2 pins. The manuscript is approved and from here on it is frozen. This phase renders it; it does not review it, re-read it, or improve a sentence on the way out.

It reads three things from `meta.json` and nothing else: `project.title`, the title the user wrote; `project.slug`, the kebab-case ASCII name that becomes the file name; `project.language`, a language tag such as `en`, `it` or `pt-BR`, which becomes the book's `lang`. The field contract is the table of `references/state.md`, and the layout is the one it defines: `book.yaml` at the project root, the rendered files under `exports/`.

This phase writes two things and no others: `book.yaml` and the files in `exports/`. No chapter, no registry, no report, no canon, no `outline.md` is touched — the export renders the approved manuscript, it does not revise it. The commands below run from the project root.

## Check pandoc first

The renderer is pandoc, and the first action of the phase is to ask for it: `pandoc --version`. Two outcomes, one of which proceeds.

Present: note the version, because a re-export years later should be explainable, then go to `## book.yaml`. A second pandoc major version is not a reason to re-verify the manuscript; it is a reason to re-run the two commands and compare the output size.

Absent: tell the user, in one message, that the markdown manuscript is complete and valid without pandoc. `manuscript/` is the book — one file per chapter, first line `# <title>` — readable in any editor, printable by conversion, and nothing in the pipeline is waiting on the export. Then give the installation pointer: pandoc is free software, downloaded from `pandoc.org` for the user's platform (an installer for Windows and macOS, a package for every Linux distribution), and once it is installed the export is the two commands of this file run once. The phase stays at `export` and the session ends there; `references/state.md` rule 9 maps both `export` and `done` to this file, so a later session resumes exactly here.

What must not happen when pandoc is missing: no alternative rendering is attempted. Not a hand-assembled EPUB out of the chapter files, not another converter offered as a stand-in for a tool known to produce the right output, not a DOCX produced so that "there is at least a file" when the user asked for an EPUB. The commands below are verified as pandoc's, and an artefact another tool produced is not the artefact this phase promises; a limitation declared is honest, a substitute quietly shipped is not.

## book.yaml

`book.yaml` is the metadata file the renderer reads, written by the orchestrator from `meta.json` — never by a subagent, following rule 1 of `references/state.md`. It holds five keys, in this order of importance:

- `title` — `project.title`, the title as the user writes it, with its accents and punctuation intact.
- `author` — the author name. `meta.json` has no such field (its `project` object is closed), so if the name is not already known the orchestrator asks the user for it HERE, once, in the user's own language. A pen name, a name with diacritics or a corporate name is written exactly as the user gives it.
- `lang` — `project.language`, copied verbatim. Not the book's source language, not the interface language, not "en" because the conversation is in English: a book in `pt-BR` ships with `lang: "pt-BR"`, and the tag is what readers and Kindle Create use for hyphenation, dictionary and text-to-speech.
- `date` — the export date, ISO `YYYY-MM-DD`, the day the files were rendered rather than the day the book was finished.
- `rights` — optional copyright line, written only when the user supplies one ("© 2026 Anna Rossi"). When the user has no preference the key is omitted; pandoc renders the book correctly without it, and an invented rights holder is worse than no rights field.

```yaml
title: "Il titolo come lo scrive l'utente"
author: "Nome Cognome"
lang: "it"
date: "2026-11-25"
rights: "© 2026 Nome Cognome"
```

The composed file is shown to the user as a preview before the export runs — the actual YAML, not a summary of it — with an invitation to correct the title, the author line or the rights text. This is the last user action before the export and it is deliberately not a gate: no `gates.*` field changes, nothing is recorded in `meta.json`, and the orchestrator does not wait for a formal approval it then has to store. The user confirms or corrects; a user who says the metadata is fine is confirmed, a user who rewrites the author line gets the line rewritten and the preview shown once more, and a user who does not care is not pressed. What the preview guarantees is that the name printed on the cover page of the EPUB is the name the user wanted, and that fact is cheap to check now and expensive to discover after distribution.

## EPUB 3 export

```bash
pandoc --from markdown --to epub3 --split-level 1 --toc \
  --metadata-file book.yaml \
  --output exports/<slug>.epub \
  manuscript/*.md
```

The command, flag by flag:

- `--from markdown --to epub3` — the chapter files are pandoc markdown and the output is EPUB 3 (the navigation document and the package metadata are the EPUB 3 ones), which is the format Kindle Create imports.
- `--split-level 1` — one document in the EPUB's spine per level-1 heading. Every chapter file opens with its title as `# <title>` (the naming rule of `references/state.md`, and the reason `references/ingest.md` insists on that first line), so one chapter becomes one EPUB file, which is what a reader's table of contents needs. It replaces the deprecated `--epub-chapter-level`, which older recipes still carry: same intent, older spelling, not to be used here.
- `--toc` — pandoc builds the table of contents from the headings, so the chapters appear in the reader's navigation in reading order.
- `--metadata-file book.yaml` — title, author, language, date and rights travel into the EPUB's package document; `lang` in particular is not decoration, it is the language the reading system reasons in.
- `manuscript/*.md` — the whole manuscript as one glob. The order is the shell's, and the names are zero-padded two-digit `NN-slug.md` files, so `01-` sorts before `02-` and `09-` before `10-`: zero-padding and glob ordering together are what guarantee chapter order in the finished book. Non-padded names would put chapter 10 after chapter 1 and before chapter 2, which is why the padding rule is not cosmetic.
- `--output exports/<slug>.epub` — `<slug>` is `project.slug`, so the same book re-exported keeps the same file name and a later version replaces the earlier one instead of accumulating beside it. If `exports/` does not exist yet, create it first with `mkdir -p exports`; pandoc writes the file, it does not create the directory.

The resulting `exports/<slug>.epub` is importable in `Kindle Create` as it stands: the user opens the application, chooses `"Import"`, and selects the file. One caveat belongs in the same breath as the command — the EPUB carries no cover. Cover design is a declared non-goal of this skill (SKILL.md stops the pipeline at export, "no KDP upload, no cover, no marketing"), and Kindle Create accepts the file without one and offers its own cover tools downstream. The orchestrator states this once, as a property of the artefact, and does not try to generate a cover image to fill the gap.

The check after the command is modest and sufficient: pandoc exited zero and `exports/<slug>.epub` exists with a plausible size — tens of kilobytes for a short book, a few megabytes for a long one; a file of a few hundred bytes is an error worth reading the pandoc output for. Inspecting the rendering chapter by chapter is not part of the phase.

## DOCX export (optional)

```bash
pandoc --from markdown --to docx --toc \
  --metadata-file book.yaml \
  --output exports/<slug>.docx \
  manuscript/*.md
```

The DOCX is optional, and it is produced on request rather than by default: for a proofreader who works in Word, for a submission that asks for `.docx`, for a reader whose device handles Word files and nothing else. When the user wants only the EPUB, this section is skipped entirely — one artefact is a complete delivery, and the phase does not require two files to be finished.

Same inputs, same metadata, same manuscript order; the differences are the ones the format implies. There is no `--split-level`, because a DOCX is one file with no spine: the whole book arrives as a single document and the chapters are level-1 headings inside it. `--toc` writes a table-of-contents field at the front, which Word populates on open or on update. And the DOCX is the format that invites editing, so it is worth saying plainly that the `.docx` is a copy for reading and markup: the manuscript in `manuscript/` stays the source, and a corrected `.docx` returned by a proofreader is a new draft to feed back through the pipeline, not an export to overwrite.

## Finish

When the export commands have run and the files are in `exports/`, the phase closes with one write to `meta.json`: `phase: "done"`. It is the last write the pipeline makes; `gates.final_approved` stays `true`, and nothing is rolled back (rule 2 of `references/state.md`, and the rule that a gate field moves only on an explicit user decision).

Then the user receives exactly two things. First, the list of files in `exports/` with their names and sizes — the artefacts that exist on disk, not a promise about them, and if the DOCX was skipped the list says so instead of leaving the user to wonder where it went. Second, the pointer into Kindle Create, because the export is where this skill's responsibility ends and the user's next step begins: open `Kindle Create`, choose `"Import"`, select `exports/<slug>.epub` from disk.

And then `the skill stops after export`. No upload to KDP, no publishing, no store metadata, no cover, no marketing copy, no "next steps" offered as a service — those are the absolute non-goals of SKILL.md, and they are not quietly performed when the user seems in a hurry or when the shop is two clicks away. If the user asks for something past the export, the answer is that the pipeline delivered the manuscript and the exports, and what happens on the store belongs to them.

`done` is terminal for the operator, not a lock on the files. A project in `done` still resolves to this file (rule 9 of `references/state.md`), so a re-export after a corrected chapter, a changed author line or a new pandoc release re-runs this phase from `## Check pandoc first`, with no gate to pass and no gate field to touch: `phase: "done"` describes the book, and `exports/` can be regenerated at any time.
