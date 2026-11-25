# Ingestion — an existing manuscript, phase `bible`

This file opens when `work_mode` is `complete`, `revise` or `restyle` and the user arrives with a manuscript already written: a `.docx` from Word, a `.pdf` exported years ago, sometimes a text file someone else prepared. The state contract stays where it belongs — `references/state.md` owns `meta.json`, its schema and its transition rules — and this file owns only the adapters and the split protocol that turn that file into chapters the pipeline can work on.
Ingestion is deliberately narrow. It brings the text in, proposes where one chapter ends and the next begins, and writes the chapter files once the user has confirmed the boundaries. It does not diagnose, it does not reconstruct the bible, and it does not repair a single sentence: the diagnostic sweep is the job of `references/reconstruction.md`, which takes over as soon as the chapters exist on disk.
Two outcomes matter and nothing else does: `research/manuscript-raw.md` exists as the raw conversion of the user's file — frozen as soon as the conversion is complete, normalization included — and `manuscript/NN-slug.md` holds one chapter per file, registered in `meta.json`. Everything the later modes do — the reconstructed bible, the revision plan, the pilot chapter, the passes — reads those chapter files, never the original binary.

## Formats and adapters

Identify the input format first, because the two common ones need completely different tools and only one of them is a pandoc job.

- `.docx` — pandoc is the primary adapter. It reads Word documents natively and produces clean GitHub-flavoured markdown, which is the closest thing to the shape the pipeline wants.
- `.pdf` — pandoc cannot read PDF as input: it writes PDF as output, it does not parse it. A `.pdf` therefore needs a dedicated text extractor, never a pandoc call.
- Already-markdown or plain text (`.md`, `.txt`) — skip conversion entirely: copy the file to `research/manuscript-raw.md` unchanged and go straight to the split.

Before announcing a plan, check what the environment actually offers. Look for pandoc in the `PATH`; for PDFs, look for the extractors listed in `## Convert .pdf`. Say what you found in one sentence, in the user's language, so the user is never surprised by a conversion that silently used a weaker tool.

When the primary adapter is missing, fall back to any converter the environment offers for that format — a word processor able to save as plain text, an office suite's command-line conversion, a library already installed — and prefer the option that preserves paragraph structure and heading levels rather than the one that is fastest. When no converter exists at all, declare the limitation explicitly to the user and ask for an alternative rather than attempting a workaround you cannot verify: exporting the file to `.docx` or to plain text is a five-minute job for the user and a guessing game for you. A manuscript that arrives in a format nothing here can read is a stop, not an occasion for improvisation.

Whatever the route, the chapters created by ingestion are registered as imported: `origin: "imported"` in `meta.json`, and `status: "imported"` when the chapter files land. That single field is how every later phase knows that prose written before this skill existed is present in the book — it is what makes `work_mode: complete` stabilize chapters 1..M before drafting M+1, and what tells `references/reconstruction.md` there is something to reconstruct.

## Convert .docx

The conversion is one command, run from the book project root so the output lands inside the project tree:

```bash
pandoc --from docx --to gfm --wrap=none --output research/manuscript-raw.md <input.docx>
```

`--from docx --to gfm --wrap=none` is the part that carries the guarantees: `gfm` keeps heading levels, emphasis and lists as markdown the pipeline can parse, and `--wrap=none` keeps one paragraph per line, so a paragraph is never mistaken for several lines and line ranges stay meaningful. `--output research/manuscript-raw.md` puts the result where the rest of the pipeline expects the raw copy; `<input.docx>` is the user's file, left untouched.

Treat `research/manuscript-raw.md` as the provenance record of what the user handed over, kept so that any later disagreement about "what the manuscript said" can be settled by looking at the conversion instead of the conversation. Provenance means the file exactly as it exits the conversion with its normalization pass done — see the next paragraph: that pass is the last write it ever receives, and from then on the file is frozen, never edited again and never deleted; the deliverable chapters are written elsewhere, in `manuscript/`.

The conversion has one last step, and it is the only write the raw file receives after pandoc produces it: a light normalization pass applied in place to `research/manuscript-raw.md` itself, not to a copy — unify heading levels so the document has a consistent structure (for example, demote every title style to `#` and every sub-heading to `##`), collapse stray blank lines, and drop empty marks such as `**` or `>` left behind by the converter. `never edit the prose` is the rule that bounds this pass — not a word changes, no typo is fixed, no sentence is reordered, no dialect normalized. When the pass ends the file is frozen: it is exactly what the chapter split below reads and what the chapter bodies are sliced from, and it is not touched again. Ingestion is transport, not editing; correcting the writing is precisely the work the passes exist to do, with the user's approval and with a registry that records every change. A silent repair at this stage would also corrupt the baseline the later passes are supposed to measure against.

If the conversion produces something unmistakably broken — every paragraph on one line, headings flattened into body text, mojibake across the whole file — say so and retry with a different converter (`.docx` to `.txt` or to `.md` via the environment) instead of normalizing by hand. Shape problems belong to the tool; text problems belong to the book.

## Convert .pdf

A `.pdf` loses the structure a `.docx` carries, so extraction is a ladder, tried in order, stopping at the first extractor that produces readable prose:

1. `pdftotext` (Poppler) — `pdftotext -layout <input.pdf> research/manuscript-raw.md` first yields a page-ordered text close to the visual layout; without `-layout` it gives plain reading-order text. Prefer the variant whose output keeps headings on their own lines.
2. Any converter the environment already offers and that can emit text or markdown from a PDF — an office suite's command line, a document-conversion service available locally, a library the user's machine ships with.
3. A Python library for text extraction, when Python and the library are present. Use it through a short script that writes the whole document to `research/manuscript-raw.md`; never route the text through a chat context to "look at it".

Whatever rung of the ladder works, the result is raw markdown in `research/manuscript-raw.md` and the discipline of `## Propose the chapter split` applies unchanged: boundaries are found mechanically, not by reading the book.

Extraction from a PDF is lossy in ways the user must hear before you rely on it: images, tables, footnotes, page headers and footers, running titles and multi-column layouts come out flattened, duplicated or missing, and hyphenation at line ends survives as broken words. That is not a defect of the pipeline, it is what the format permits — the words are there, the shape is not. So when a PDF is the only source, declare the limitation at the start, in plain terms: what survived well (the prose), what probably did not (tables, figures, notes), and what that implies for the chapter boundaries you are about to propose. If the extracted text is so degraded that a chapter cannot be delimited, ask the user for a `.docx` or a text export of the same manuscript: the honest request is cheaper than a reconstruction of a lost layout.

## Propose the chapter split

The manuscript is one long file; the pipeline works one chapter per file. Deciding where the cuts go is a proposal you make and a decision the user owns. Do the mechanical part of it without ever holding the manuscript in your context: `research/manuscript-raw.md` can be tens of thousands of lines, and reading it whole is exactly the failure this file exists to prevent.

Boundaries are found by `heading search or line ranges` — nothing else. In practice:

- Search for structure: grep for level-1 and level-2 markdown headings, for the usual chapter markers (`Chapter`, `Capitolo`, `Chapitre`, `Capítulo`, a bare number on its own line), and for form-feed characters or repeated page furniture that mark page breaks in the extracted text.
- Work on numbers, not on text: `grep -n` gives the line numbers of the candidates, `wc -w` over a line range gives the mechanical word count of a section, `sed -n 'A,Bp'` reads only the few lines around a candidate boundary. That is the full extent of what you look at.
- When the evidence conflicts — headings on some chapters and not on others — fall back to line ranges: measure the file's length, see whether chapters cluster at a regular distance, and treat equal-sized blocks as a hypothesis to refine, not as an answer.

The cardinal rule, and the reason this section exists: never read `research/manuscript-raw.md` in full, and never paste a large slice of it into a prompt, a subagent dispatch or your own reasoning. You MUST obtain every boundary, every title guess and every word count mechanically, from line numbers, and look at no more than the handful of lines needed to name a chapter. The whole point of the split step is to keep a book-sized artefact out of a context window that will be needed later to keep a book-sized project coherent.

Then propose the split to the user, in their language, as a numbered list — one entry per chapter:

- the number and the proposed title, taken from the heading when one exists and from the first line when it does not;
- the first line of the chapter, quoted briefly (one short line, not a paragraph), so the user can recognize the cut at a glance;
- the word count of the range, counted mechanically, not estimated;
- anything that needs a decision: a prologue with no heading, two chapters that the headings merge into one, a part title that is not a chapter.

Ask one question at a time about whatever is ambiguous, and iterate. Front matter, dedications, tables of contents, backwards prefaces and appendices are all legitimate things to keep in the raw file and out of `manuscript/`: name them in the proposal and let the user decide, rather than deciding silently.

The loop ends on one condition only: the user confirms the chapter split. Not a plausible-looking proposal, not a silence read as consent, not an "I'll start and we'll fix it later" — the boundaries the user confirms are the boundaries written to disk, because a wrong cut is expensive afterwards: it misnumbers every chapter after it, corrupts the provenance `[ch.NN]` recorded in the facts index, and invalidates a bible reconstructed against the wrong units. If the user is unsure, show the two or three candidate cuts in words and let them choose; the confirmation is a gate, and gates in this pipeline are always explicit.

## Write the chapter files

Once the split is confirmed, write one file per chapter under `manuscript/`, named `manuscript/NN-slug.md`:

- `NN` is the chapter number, two digits zero-padded, `01` to `99` — the numbering is contiguous from `01` and matches `chapters[].number` in `meta.json` (invariant C1 of `references/state.md`).
- `slug` is a kebab-case ASCII slug of the chapter title: lowercase, hyphens between words, accents stripped, punctuation dropped (`La città di nebbia` becomes `citta-di-nebbia`). Transliterate accented and non-Latin titles; when transliteration would be unreliable or unreadable, fall back to `chapter-NN` and keep the real title in the file and in `meta.json`. The full naming rules live in `references/state.md` and are the authority when they disagree with this paragraph.
- the first line of every chapter file is its title as a level-1 heading, `# <title>`, exactly — the pipeline, the passes and the export all rely on that one heading to find the chapter's name.

The body is the confirmed line range of `research/manuscript-raw.md`, copied verbatim, with the heading the user confirmed as the title. The mapping is mechanical: a small script that slices ranges and writes files is the right tool, and it costs nothing in context. `never edit the prose` applies here too, in its strongest form — not one character is added, removed or reordered between the raw file and the chapter file, beyond the level-1 heading the naming rule requires.

Then register the chapters in `meta.json`: one `chapters[]` entry per file with `number`, `file`, `title`, `status: "imported"` and `origin: "imported"`. This write is yours alone — `meta.json` is written only by the orchestrator, never by a subagent, and never by the script that sliced the files. When the entries land, `chapters` stops being `[]`, which is the state `references/state.md` tolerates only until Gate 1.

Registration does not move the phase. `phase` stays `bible`, because importing a manuscript is not an approval: the bible and outline still have to be reconstructed from this text and validated by the user at Gate 1, and until that gate nothing in the pipeline may advance (invariant C2). The stabilization block of `work_mode: complete` is likewise untouched here — it is set before drafting, after the reconstruction.

With the chapters imported, this file's work is done and the next file is `references/reconstruction.md`: the diagnostic sweep that reads the chapters one at a time, reconstructs the bible, the style guide and the facts index from them, and prepares the gate the user will validate. Do not start that sweep here, and do not summarize the manuscript on the way out — hand over the registered chapters and let the reconstruction do its own reading, mechanically bounded like everything else in this pipeline.
