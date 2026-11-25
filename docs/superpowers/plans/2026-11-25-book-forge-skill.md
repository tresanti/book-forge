# book-forge — Piano di implementazione della skill

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Costruire la skill pubblica `book-forge` — dalla spec congelata FREEZE OK un repo GitHub installabile che accompagna la scrittura/correzione di un libro fino all'export EPUB/DOCX, con colloquio, bibbia, ciclo capitolo a gate umano e passate di correzione a subagenti.

**Architecture:** Repo con layout skills.sh (`skills/book-forge/`). `SKILL.md` sottile = macchina a stati + dispatch dei ruoli (progressive disclosure: la conoscenza per fase vive in `references/*.md`; i prompt di ruolo — plain markdown harness-agnostic — in `references/roles/*.md`). Stato del libro su disco (`meta.json` nel progetto utente) per la riprendibilità. Tooling dev-only: `tests/check.py` (Python via uv, stdlib + jsonschema) che congella contratti e ancoraggi dei warning W1–W5 come controlli meccanici.

**Tech Stack:** Markdown (Agent Skills spec); Python ≥3.11 via **uv** (dev-only: `pyproject.toml` con `package = false`, dipendenza `jsonschema`); GitHub Actions (uv in CI); pandoc documentato per ingest/export ma NON richiesto dal nucleo (nessun task lo esegue: non è installato su questa macchina).

**Spec:** `docs/superpowers/specs/2026-11-25-book-forge-design.md` — CONGELATA, verdetto oracle **FREEZE OK round 2**. Il piano la attua integralmente incluse le eccezioni protette, la matrice Fasi×Lavori e le decisioni utente 1–12. L'autorità è la spec; le stringhe pinnate qui sono vincolanti per il worker.

## Verifiche fatte prima della stesura (stessa macchina, 2026-11-25)

- **uv 0.13.5 + CPython 3.13.17**: provato con scratch nel repo — `pyproject.toml` con `[tool.uv] package = false`, `uv run <script>`, jsonschema draft 2020-12 (`jsonschema.validators.validator_for`, `check_schema`, `iter_errors`), istanza invalida rifiutata correttamente. Gli snippet di codice dei Task 2 e 4 sono questi, provati.
- **`python` del PATH è lo stub dello Store**: TUTTI i comandi Python del piano passano da `uv run`. Mai `python`/`pytest` nudi.
- **Pandoc NON installato localmente**: nessun task lo esegue. Flag di export verificati sulla documentazione ufficiale (Context7): `-t epub3`, `--split-level 1` (sostituisce il deprecato `--epub-chapter-level`), `--toc` (ha effetto sui formati standalone — EPUB e DOCX lo sono), `--metadata-file`, `--epub-cover-image` (non usato: cover design è un non-goal).
- **pi**: discovery ricorsiva delle directory contenenti `SKILL.md`; location Agent Skills `~/.agents/skills/` supportata; frontmatter Agent Skills: name ≤64 caratteri lowercase/kebab, description ≤1024. (da `docs/skills.md` di pi 1.6.0)
- Repo attuale: 2 commit (spec congelata + dossier oracle), `.gitignore` esiste, niente codice.

## Warning oracle → task (W1–W5 attuati)

| Warning | Come è attuato | Verifica meccanica |
|---|---|---|
| **W1** — role paths iniettati nei prompt + re-lettura `references/<fase>.md` a ogni resume | Task 3: SKILL.md (tabella dispatch con i path `references/roles/*.md`; regola di resume) | Substrings Task 3; `check_role_paths` del Task 13 (paths citati in SKILL.md == file esistenti, nessuno mancante/extra) |
| **W2** — .docx→pandoc, .pdf→estrattore dedicato, conferma utente dello split | Task 6: `references/ingest.md` | Substrings Task 6 (`pandoc cannot read PDF`, `user confirms`, comando esatto) |
| **W3** — layout `skills/book-forge/` + description circoscritta | Task 1 (albero), Task 3 (frontmatter + description nel dominio libro/manoscritto) | `check_frontmatter` (Task 2 core) + fixtures della description |
| **W4** — coda `grammatica→ortografia` per restyling; sottoinsieme di stabilizzazione per completamento | Task 11 `passes.md` (code/ambiti per modalità) + invariante C6 (Task 4) sulle fixture | Substrings Task 11; fixture `meta-restyhe…`/`meta-revise…` + `check_meta_invariants` |
| **W5** — final-review = subagent freschi per capitolo + aggregazione dei soli report; `facts-index.md` risincronizzato dopo modifiche struttura/canon | Task 13 `final-review.md` (`reports/final-review/ch-NN.md` per capitolo, orchestratore aggrega); Task 11 `passes.md` sezione `## facts-index resync` | Substrings Task 13 + header Task 11; substring `resync` |

## "Cosa resta al builder" → task (tutte le decisioni libere sono prese qui)

| Decisione libera (spec) | Task | Decisione pinnata |
|---|---|---|
| Question bank per profilo | 5 | Protocollo una-domanda-per-volta; prima domanda obbligatoria = modalità di validazione; topic core + 3× profilo (§ Task 5) |
| Template bibbia per profilo | 7 | 3 template con campi minimi [min] vs opzionali [opt]; style guide normativa inclusa |
| Wording prompt di ruolo | 9, 10, 12, 13 | 6 role file con struttura fissa `Identity / Inputs / Routine (o Duty) / Output contract / Never` + invarianti comportamentali per ciascuno |
| Formato ledger di continuità | 8 | `facts-index.md` = tabella 6 colonne con provenienza `[ch.NN]`; window scorrevole K=`continuity_window` (default 3) |
| Manifesto passate | 11 | Ordine macro→micro pinnato; per-passata: cosa cerca/tocca/non tocca/come registra; registri `passes/registry-<pass>.md` |
| Dettagli pandoc | 14 | `book.yaml` + comandi esatti EPUB3/DOCX (Task 14) |
| Layout repo + istruzioni installazione | 1, 15 | Albero Task 1; README Task 15 (skills.sh / pi / Claude Code) |
| Euristica lunghezza capitolo | 7 | Tabella numerica per profilo target (§ Task 7) |
| `meta.json` schema + regole avanzamento | 4 | Schema JSON completo + 8 invarianti C1–C8 + regole di transizione in `state.md` |

## Global Constraints

1. **Lingua**: artefatti della skill in **inglese**; colloquio (fase 0) nella lingua dell'utente; manoscritto e artefatti di progetto (bible, outline, ledger…) nella **lingua del libro** (`project.language`). La question bank come artefatto è inglese (spec Vincoli / builder-check 7).
2. **W3 layout**: la skill vive in `skills/book-forge/` (repo skills.sh); `name: book-forge` = nome directory; `description` in frontmatter ≤1024 caratteri, circoscritta al dominio libro/manoscritto (del testo Task 3, vincolante).
3. **Ruoli harness-agnostic**: i file `references/roles/*.md` sono prompt in prosa ("you are…"), NON nominano tool di un harness; è `SKILL.md` che mappa ruolo→meccanismo del host (pi subagent / Claude Code Task / inline). Anti-goal della spec: dipendere da nomi di agenti custom.
4. **Economia di contesto**: mai il libro intero in un contesto; un capitolo .md per subagent; structure/continuity operano per capitolo in sequenza contro il ledger.
5. **Gate umani hard**: nessun capitolo avanza senza lettura/approvazione dell'utente; nessuna fase avanza senza il gate corrispondente (`gates.*` in meta.json, invariante C2). Riscrittura immediata + ri-lettura nello stesso capitolo (decisione utente 3).
6. **Copyright**: ogni testo riportato da fonti esterne porta SEMPRE fonte (URL + data di accesso); riscrittura con parole proprie SOLO su richiesta esplicita (decisione utente 6; obiettivo 5).
7. **meta.json**: lo scrive SOLO l'orchestratore (main agent); ogni role file contiene il divieto `do not write meta.json` (substring pinnata).
8. **Passate**: ordine fisso macro→micro `structure → continuity → style/voice → grammar → spelling`; chiave interna passate: `structure, continuity, style, grammar, spelling`; per-file per le micro, per-capitolo sequenziali per structure/continuity (decisione utente 12 / B1).
9. **Contraddizioni**: auto-fix SOLO su canon univoco dalla bibbia validata, e tocca SOLO i capitoli in errore; canon ambiguo → STOP + decisione utente (`passes/contradiction-NN.md`); il ledger non muta mai con scelte arbitrarie prima del gate (B2).
10. **Gate finale**: `final_review` con fresh session— in inline: stop `awaiting_fresh_session=true`; override self-review solo esplicito → `degraded_non_independent=true` nel rapporto (B4).
11. **File/Naming**: UTF-8, LF; capitoli `manuscript/NN-slug.md` (NN 2 cifre, 01–99), primo header di livello 1 `# <titolo>`; slug lowercase kebab-case.
12. **Tooling dev**: uv + Python ≥3.11 (`pyproject.toml`, `[tool.uv] package = false`, dip `jsonschema>=4.23`, `uv.lock` committato). Comandi test SEMPRE `uv run tests/check.py`. Nessuna dipendenza per l'utente della skill; pandoc opzionale (ingest docx / export).
13. **Commit**: un commit per task (messaggi pinnati); il piano si esegue su branch di lavoro (worktree se si usa subagent-driven-development), non direttamente su `main`.
14. **Stringhe pinnate**: ogni REQUIRED_SUBSTRINGS/REQUIRED_HEADERS di `tests/check.py` è contratto: il worker li copia ESATTI. Le chiavi_metriche/artefatti inglesi sono le stesse citate dalla spec tradotta (ex. `[ch.NN]` per la provenienza, StatusBar `pass_scope`…).

## Review Focus

Le cinque classi di fallimento più probabili all'uso, con il test che le aggancia al task che ne è proprietario:

1. **Resume con memoria stale** — il progetto si riprende dopo mesi e l'agente "ricorda" la fase invece di rileggerla: ogni resume DEVE rileggere `meta.json` + `references/<phase>.md`. → Task 3 substrings (`Read `references/<phase>.md``, `never trust session memory`) + header `## Phase machine`.
2. **Dispatch su ruolo inesistente** — path di ruolo digitato male in SKILL.md → subagent senza prompt di ruolo. → Task 13 `check_role_paths`: paths citati in SKILL.md == unione dei 6 role file esistenti, nessuno mancante né extra.
3. **Bypass dei gate** — avanzamento fase senza approvazione utente (es. `phase=passes` con bibbia non approvata; self-review spacciata per indipendente). → Task 4: invariante C2 (fixtures `meta-invalid-gates.json`, `meta-invalid-flags.json`) e C3 (flags mutuamente esclusivi).
4. **Auto-fix oltre il mandato + ledger stale** — contraddizione con canon ambiguo "risolta" arbitrariamente; `facts-index.md` non risincronizzato dopo la passata struttura o auto-fix di canon. → Task 11 substrings (`only the chapters in error`, `stop and ask the user`) + header `## facts-index resync`.
5. **Scope passate sbagliato per modalità** — restyling senza coda grammatica→ortografia; completamento che scrive M+1 senza stabilizzazione di 1..M (W4). → Task 11 substrings (`style/voice → continuity → grammar → spelling`, `structure and continuity`) + Task 4 invariante C5 (`stabilization`) e C6 (scope per work_mode) pinnate sulle fixture.

---

## Struttura file del repo (decisione di decomposizione)

```
book-forge/                              # repo GitHub (nome: book-forge, vedi README)
├── README.md                            # Task 15
├── LICENSE                              # Task 1 (MIT)
├── pyproject.toml                       # Task 1 (dev-only, uv)
├── uv.lock                              # Task 1 (generato da uv, committato)
├── .gitignore                           # Task 1 (aggiunta .venv/, __pycache__/)
├── .github/workflows/ci.yml             # Task 1
├── tests/
│   ├── check.py                         # Task 2 core; esteso nei Task 4 e 13
│   └── fixtures/                        # Task 4 (12 fixture meta.json)
└── skills/
    └── book-forge/
        ├── SKILL.md                     # Task 3 — macchina a stati + dispatch (W1, W3)
        └── references/
            ├── state.md                # Task 4 — schema meta.json + regole transizione + resume
            ├── meta.schema.json         # Task 4 — JSON Schema draft 2020-12 (autorità macchina)
            ├── intake.md               # Task 5 — fase 0 colloquio
            ├── ingest.md               # Task 6 — ingestione manoscritto esistente (W2)
            ├── bible.md                # Task 7 — fase 1 creazione: template bibbia ×3 + outline + euristica
            ├── ledger.md               # Task 8 — facts-index + handoff window
            ├── reconstruction.md       # Task 9 — fase 1 per lavori (ii)/(iii)/(iv)
            ├── drafting.md             # Task 10 — fase 2 ciclo capitolo
            ├── passes.md               # Task 11 — fase 3 motore di correzione (W4, W5, B1, B2)
            ├── final-review.md         # Task 13 — fase 4 gate finale (B4, W5)
            ├── export.md               # Task 14 — fase 5 pandoc
            └── roles/
                ├── researcher.md       # Task 9
                ├── drafter.md          # Task 10
                ├── structure-editor.md     # Task 12
                ├── continuity-checker.md   # Task 12
                ├── copy-editor.md          # Task 12
                └── final-reviewer.md       # Task 13
```

Progetto libro UTENTE (creato a runtime dalla skill, NON in questo repo) — source of truth pinnata in `state.md`:

```
<book-project>/
├── meta.json            # stato pipeline (schema references/meta.schema.json)
├── bible.md             # canon: premise, personaggi/mondo o concetti/promesse, style guide, glossario
├── outline.md           # TOC + contratto per capitolo
├── manuscript/          # 01-slug.md, 02-slug.md… un file per capitolo
├── continuity/
│   ├── facts-index.md   # indice fatti/entità/promesse con provenienza [ch.NN]
│   └── window/          # NN-slug.md — K handoff più recenti (K = meta.continuity_window)
├── research/            # materiale grezzo; sources.md (URL + data di accesso)
├── passes/
│   ├── registry-structure.md / registry-continuity.md / registry-style.md / registry-grammar.md / registry-spelling.md
│   └── contradiction-01.md …   # file di STOP per canon ambiguo
├── reports/
│   ├── final-review/ch-NN.md   # report per capitolo (Task 13, W5)
│   └── final-review.md         # rapporto aggregato
├── revision-plan.md     # solo work_mode revise — piano di revisione approvato al Gate 1
├── pilot.md             # solo work_mode restyle — capitolo pilota riscritto (ancora few-shot)
├── book.yaml            # metadati export (fase 5)
└── exports/             # <slug>.epub, <slug>.docx
```

Routing fase→file (pinnato; SKILL.md lo replica): `intake→intake.md`; `bible→bible.md` (mode create) / `ingest.md` (esistenti, `chapters == []`) / `reconstruction.md` (esistenti, capitoli importati); `chapters→drafting.md`; `passes→passes.md`; `final_review→final-review.md`; `export→export.md`; `done→export.md`.

---

### Task 1: uv project scaffold + CI

**Files:**
- Create: `pyproject.toml`, `.github/workflows/ci.yml`, `LICENSE`
- Generate: `uv.lock`
- Modify: `.gitignore` (append)

**Interfaces:**
- Produces: ambiente uv con dipendenza `jsonschema>=4.23` (consumata dal Task 4); comando `uv run tests/check.py` (ancora inesistente a questo task: lo crea il Task 2); `.venv` ignorata.

- [ ] **Step 1: Create `pyproject.toml` (contenuto esatto)**

```toml
[project]
name = "book-forge-dev"
version = "0.1.0"
description = "Development checks for the book-forge skill repository. Not shipped with the skill."
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.23"]

[tool.uv]
package = false
```

- [ ] **Step 2: Append a `.gitignore`**

```gitignore
.venv/
__pycache__/
```

- [ ] **Step 3: Create `LICENSE`** — testo standard MIT con riga copyright: `Copyright (c) 2026 The book-forge authors`.

- [ ] **Step 4: Create `.github/workflows/ci.yml` (contenuto esatto)**

```yaml
name: checks
on:
  push:
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync --frozen
      - run: uv run tests/check.py
```

- [ ] **Step 5: Genera `uv.lock` e verifica l'ambiente**

Run: `uv lock && uv run python -c "import jsonschema, sys; print(sys.version_info[:2], jsonschema.__version__)"`
Expected: file `uv.lock` creato; stampa la tupla Python (≥(3, 11)) e la versione jsonschema (≥4.23).

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock .gitignore LICENSE .github/workflows/ci.yml
git commit -m "chore: uv project scaffold + CI (dev-only tooling)"
```

### Task 2: tests/check.py — harness strutturale (core)

**Files:**
- Create: `tests/check.py`

**Interfaces:**
- Produces: harness eseguibile con `uv run tests/check.py`; registri che i task successivi popoleranno — nomi vincolanti: `REQUIRED_FILES: list[str]`, `REQUIRED_HEADERS: dict[str, list[str]]`, `REQUIRED_SUBSTRINGS: dict[str, list[str]]`, `FIXTURES_VALID`, `FIXTURES_INVALID` (Task 4), `ROLE_FILES` + `check_role_paths` (Task 13). Ogni check fallito produce errori testuali `"<rel>: <problema>"` e exit 1.

- [ ] **Step 1: Create `tests/check.py` (contenuto esatto — core stdlib)**

```python
#!/usr/bin/env python
"""Structural checks for the book-forge skill repository.

Core = stdlib only. Task 4 adds JSON-Schema validation (jsonschema,
declared in pyproject.toml) and Task 13 adds role-path integrity.
Run: uv run tests/check.py  — exit 1 lists every problem.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---- expectations registry (grow with tasks; exact values are binding) ----

REQUIRED_FILES: list[str] = []

REQUIRED_HEADERS: dict[str, list[str]] = {
    # "repo/relative.md": ["## Exact header", ...]
}

REQUIRED_SUBSTRINGS: dict[str, list[str]] = {}

FRONTMATTER_LINES: dict[str, list[str]] = {
    "skills/book-forge/SKILL.md": ["name: book-forge"],
}
DESCRIPTION_MAX = 1024

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+?)\)")
URL_RE = re.compile(r"^[a-z][a-z0-9+.-]*://")
FENCE_RE = re.compile(r"`{3,}.*?`{3,}", re.DOTALL)
SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.*?)(?<!`)\1(?!`)", re.DOTALL)

# ---- checks ----------------------------------------------------------------


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def check_required_files(errors: list[str]) -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"missing file: {rel}")


def check_frontmatter(errors: list[str]) -> None:
    for rel, required in FRONTMATTER_LINES.items():
        if not (ROOT / rel).is_file():
            continue  # reported when listed in REQUIRED_FILES
        lines = read(rel).splitlines()
        if not lines or lines[0] != "---":
            errors.append(f"{rel}: missing YAML frontmatter")
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            errors.append(f"{rel}: frontmatter not closed")
            continue
        fm = lines[1:end]
        for line in required:
            if line not in fm:
                errors.append(f"{rel}: frontmatter missing {line!r}")
        for line in fm:
            if line.startswith("description:"):
                value = line[len("description:"):].strip()
                if len(value) > DESCRIPTION_MAX:
                    errors.append(f"{rel}: description over {DESCRIPTION_MAX} chars")
                break
        else:
            errors.append(f"{rel}: frontmatter missing description")


def check_headers(errors: list[str]) -> None:
    for rel, wanted in REQUIRED_HEADERS.items():
        if not (ROOT / rel).is_file():
            continue
        have = {ln.strip() for ln in read(rel).splitlines() if ln.startswith("## ")}
        for header in wanted:
            if header not in have:
                errors.append(f"{rel}: missing heading {header!r}")


def check_substrings(errors: list[str]) -> None:
    for rel, wanted in REQUIRED_SUBSTRINGS.items():
        if not (ROOT / rel).is_file():
            continue
        text = read(rel)
        for needle in wanted:
            if needle not in text:
                errors.append(f"{rel}: missing pinned string {needle!r}")


def strip_code(text: str) -> str:
    """Drop fenced code blocks and variable-length inline code spans — the
    link-check judges prose markdown, never link examples quoted inside code
    (including double-backtick spans that quote code containing backticks)."""
    return SPAN_RE.sub(" ", FENCE_RE.sub(" ", text))


def check_links(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts or "node_modules" in path.parts or "graphify-out" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        for target in LINK_RE.findall(strip_code(read(rel))):
            if URL_RE.match(target) or target.startswith("/"):
                continue  # remote URLs and repo-absolute links: out of scope
            target = target.split("#", 1)[0]
            if not target:
                continue  # pure anchor
            if not (path.parent / target).is_file():
                errors.append(f"{rel}: broken link -> {target}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_frontmatter(errors)
    check_headers(errors)
    check_substrings(errors)
    check_links(errors)
    if errors:
        print(f"FAIL — {len(errors)} problem(s)")
        for e in errors:
            print(f" - {e}")
        return 1
    print("OK — all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Smoke dell'harness**

Run: `uv run tests/check.py`
Expected: `OK — all checks passed` (registri vuoti; frontmatter-check su SKILL.md ancora inesistente → skippato; link-check gira sui .md di `docs/` DOPO `strip_code`: gli esempi tra backtick o dentro fence NON sono link da validare — piano e verbali contengono esempi inline-code legittimi, vedi Amendamento 4).

- [ ] **Step 3: Smoke negativo — fidarsi dell'harness**

Aggiungere TEMPORANEAMENTE una riga `"docs/does-not-exist.md"` a `REQUIRED_FILES`, run: `uv run tests/check.py` → Expected: `FAIL — 1 problem(s)` con `missing file: docs/does-not-exist.md`. Rimuovere la riga e rilanciare → Expected: `OK — all checks passed`.

- [ ] **Step 4: Commit**

```bash
git add tests/check.py
git commit -m "test: structural harness for the skill repo (check.py core)"
```

### Task 3: skills/book-forge/SKILL.md — macchina a stati + dispatch (W1, W3)

**Files:**
- Create: `skills/book-forge/SKILL.md`
- Modify: `tests/check.py` (solo registri)

**Interfaces:**
- Consumes: harness del Task 2 (registri); schema enum meta del Task 4 — usare qui i VALORI pinnati nel Task 4 (`work_mode`: `create|complete|revise|restyle`; `phase`: `intake|bible|chapters|passes|final_review|export|done`; ruoli della tabella spec).
- Produces: `skills/book-forge/SKILL.md` con frontmatter e mapping fase→file e ruolo→path che TUTTI i task successivi rispettano; le path `references/roles/*.md` citate qui sono esattamente le 6 di `ROLE_FILES` del Task 13.

- [ ] **Step 1: Aggiungere a `tests/check.py` (dati, esatti)**

`REQUIRED_FILES` += `["skills/book-forge/SKILL.md"]`

`REQUIRED_HEADERS["skills/book-forge/SKILL.md"]` =
```python
[
    "## First action — read the state",
    "## Phase machine",
    "## Routing by work_mode",
    "## Dispatching roles",
    "## Never",
]
```

`REQUIRED_SUBSTRINGS["skills/book-forge/SKILL.md"]` =
```python
[
    "Read `references/<phase>.md`",
    "never trust session memory",
    "references/roles/researcher.md",
    "references/roles/drafter.md",
    "references/roles/structure-editor.md",
    "references/roles/continuity-checker.md",
    "references/roles/copy-editor.md",
    "references/roles/final-reviewer.md",
    "references/ingest.md",
    "awaiting_fresh_session",
    "degraded_non_independent",
    "one question at a time",
    "user confirms the chapter split",
]
```

- [ ] **Step 2: Run per verificare il fallimento atteso**

Run: `uv run tests/check.py`
Expected: `FAIL` — `missing file: skills/book-forge/SKILL.md` (e gli altri check skippati).

- [ ] **Step 3: Scrivere `skills/book-forge/SKILL.md`**

Frontmatter e sezioni — contenuti prescritti:

```markdown
---
name: book-forge
description: Write or revise a full book manuscript — novel or nonfiction — from an idea or an existing draft to an exportable EPUB/DOCX. Use when the user wants to write a book, continue or complete a partial manuscript, correct and professionally edit an existing book (even one written without this skill), or restyle a finished book with a new voice.
---
```

Sezioni (header `## ` esatti come nel registro; contenuto: 4–10 righe per sezione):

1. Intro (PRIMA di `## First action…`, senza header `##`): 3 righe — cosa fa (4 lavori auto-rivelati), cosa produce, che si ferma all'export.
2. `## First action — read the state`: se esiste `<project>/meta.json` → leggilo, poi `references/state.md`, poi la reference della fase corrente: `Read `references/<phase>.md`` — sempre RILETTO a ogni session/resume, mai dalla memoria: frase esatta `never trust session memory` (W1); `<phase>` si risolve SEMPRE con la tabella di routing `phase × work_mode` del punto 3 (mai nome file letterale: `final_review` → `final-review.md`; `bible` esistente → `ingest.md` o `reconstruction.md` a seconda dei capitoli registrati). Se non esiste → inizia da `references/intake.md` (fase 0). Progetto assente → chiedere all'utente dove crearlo/aprirlo.
3. `## Phase machine`: tabella 7 righe `phase → reference file → gate → esecutori` (routing pinnato nella sezione "Struttura file" di questo piano + regola 9 di state.md): intake→intake.md (gate: domande completate; inline), bible→bible.md (create) | ingest.md (esistenti, `chapters == []`) | reconstruction.md (esistenti, capitoli importati) (gate: bible_approved; researcher subagent + utente; per i lavori su esistente la fase bible COMINCIA da ingest.md e continua su reconstruction.md appena i capitoli sono importati), chapters→drafting.md (gate: per-capitolo utente; drafter subagent), passes→passes.md (gate: passes_approved via protocollo (b); editor subagent), final_review→final-review.md (gate: final_approved; final-reviewer FRESCO per capitolo), export→export.md (nessun gate; inline + pandoc), done.
4. `## Routing by work_mode`: la Matrice Fasi × Lavori della spec in forma compatta: 4 righe (create/complete/revise/restyle) × fasi sì/no + note di stabilizzazione (complete: structure+continuity su 1..M PRIMA di M+1), restyle (vecchio libro rilascia SOLO canon/facts/ledger; pilota come ancora few-shot; coda fase 3 = style/voice → continuity → grammar → spelling).
5. `## Dispatching roles`: (a) regola W1: OGNI dispatch di subagent include nel prompt la path del role file (tabella ruolo→path: researcher, drafter, structure-editor, continuity-checker, copy-editor, final-reviewer) + i file di input per quel compito; (b) mapping harness: pi→subagent tool, Claude Code→Task tool, altrimenti inline nello stesso ordine; (c) due eccezioni protette: gate finale → `awaiting_fresh_session` (stop hard, sessione nuova; override self-review solo esplicito → `degraded_non_independent` nel rapporto), Researcher senza accesso web → lo dichiara subito e lavora sul materiale utente; (d) regola colloquio: one question at a time, nella lingua dell'utente; (e) ingest: user confirms the chapter split.
6. `## Never`: lista anti-goal: avanzare un capitolo senza gate umano; caricare il libro intero in un contesto; testo copiato senza fonte; subagenti che scrivono `meta.json`/`bible.md`/ledger fuori contratto; proseguire oltre l'export (upload KDP).

Disciplina link-check (vincolante): tutti i path `references/…` e `references/roles/*.md` in SKILL.md si scrivono come INLINE CODE tra backtick, MAI come hyperlink markdown — i file di riferimento esistono solo dai Task 4–13 e `check_links` (Task 2) segnala link rotti allo Step 4 di questo task; `check_role_paths` (Task 13) li riconosce da qualsiasi formattazione.

- [ ] **Step 4: Run per verificare che passi**

Run: `uv run tests/check.py`
Expected: `OK — all checks passed`. La description del frontmatter ≤1024 (check attivo dal Task 2).

- [ ] **Step 5: Commit**

```bash
git add skills/book-forge/SKILL.md tests/check.py
git commit -m "feat(skill): SKILL.md state machine + role dispatch (W1, W3)"
```

### Task 4: meta.schema.json + state.md + fixture + validazione

**Files:**
- Create: `skills/book-forge/references/state.md`, `skills/book-forge/references/meta.schema.json`, `tests/fixtures/meta-*.json` (12 file)
- Modify: `tests/check.py` (registri + sezione schema)

**Interfaces:**
- Consumes: harness core del Task 2; snippet jsonschema verificati in pre-piano (validator_for/check_schema/iter_errors).
- Produces: contratto `meta.json` usato da TUTTI i content successivi — campi esatti: `schema_version`, `project{title,slug,language,created}`, `work_mode`, `genre_profile`, `validation_mode{type,block_size}`, `phase`, `flags{awaiting_fresh_session,degraded_non_independent,web_available}`, `gates{bible_approved,passes_approved,final_approved}`, `chapters[{number,file,title,status,origin}]`, `continuity_window`, `length_target{words,chapters}`, `stabilization{structure,continuity}`, `pass_scope`, `pass_progress`, `notes`. Enum pinnati: `work_mode: create|complete|revise|restyle`; `genre_profile: fiction|practical_nonfiction|narrative_nonfiction`; `validation_mode.type: chapter|blocks`; `phase: intake|bible|chapters|passes|final_review|export|done`; `chapters.status: planned|imported|drafting|user_review|approved`; `chapters.origin: written|imported`; passate: `structure|continuity|style|grammar|spelling`; progress: `pending|in_progress|done`.

- [ ] **Step 1: Create `skills/book-forge/references/meta.schema.json` (contenuto esatto)**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://book-forge.dev/skills/book-forge/meta.schema.json",
  "title": "book-forge project meta.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "project", "work_mode", "genre_profile", "validation_mode", "phase", "flags", "gates", "chapters", "continuity_window"],
  "properties": {
    "schema_version": { "const": 1 },
    "project": {
      "type": "object",
      "additionalProperties": false,
      "required": ["title", "slug", "language", "created"],
      "properties": {
        "title": { "type": "string", "minLength": 1 },
        "slug": { "type": "string", "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$" },
        "language": { "type": "string", "pattern": "^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$" },
        "created": { "type": "string", "format": "date" }
      }
    },
    "work_mode": { "enum": ["create", "complete", "revise", "restyle"] },
    "genre_profile": { "enum": ["fiction", "practical_nonfiction", "narrative_nonfiction"] },
    "validation_mode": {
      "type": "object",
      "additionalProperties": false,
      "required": ["type"],
      "properties": {
        "type": { "enum": ["chapter", "blocks"] },
        "block_size": { "type": "integer", "minimum": 2 }
      },
      "if": { "properties": { "type": { "const": "blocks" } }, "required": ["type"] },
      "then": { "required": ["block_size"] }
    },
    "phase": { "enum": ["intake", "bible", "chapters", "passes", "final_review", "export", "done"] },
    "flags": {
      "type": "object",
      "additionalProperties": false,
      "required": ["awaiting_fresh_session", "degraded_non_independent", "web_available"],
      "properties": {
        "awaiting_fresh_session": { "type": "boolean" },
        "degraded_non_independent": { "type": "boolean" },
        "web_available": { "type": ["boolean", "null"] }
      }
    },
    "gates": {
      "type": "object",
      "additionalProperties": false,
      "required": ["bible_approved", "passes_approved", "final_approved"],
      "properties": {
        "bible_approved": { "type": "boolean" },
        "passes_approved": { "type": "boolean" },
        "final_approved": { "type": "boolean" }
      }
    },
    "chapters": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["number", "file", "title", "status", "origin"],
        "properties": {
          "number": { "type": "integer", "minimum": 1, "maximum": 99 },
          "file": { "type": "string", "pattern": "^manuscript/\\d{2}-[a-z0-9]+(-[a-z0-9]+)*\\.md$" },
          "title": { "type": "string" },
          "status": { "enum": ["planned", "imported", "drafting", "user_review", "approved"] },
          "origin": { "enum": ["written", "imported"] }
        }
      }
    },
    "continuity_window": { "type": "integer", "minimum": 2, "maximum": 10 },
    "length_target": {
      "type": ["object", "null"],
      "additionalProperties": false,
      "properties": {
        "words": { "type": ["integer", "null"] },
        "chapters": { "type": ["integer", "null"] }
      }
    },
    "stabilization": {
      "type": ["object", "null"],
      "additionalProperties": false,
      "required": ["structure", "continuity"],
      "properties": {
        "structure": { "enum": ["pending", "in_progress", "done"] },
        "continuity": { "enum": ["pending", "in_progress", "done"] }
      }
    },
    "pass_scope": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": { "enum": ["structure", "continuity", "style", "grammar", "spelling"] }
    },
    "pass_progress": {
      "type": "object",
      "additionalProperties": false,
      "patternProperties": {
        "^(structure|continuity|style|grammar|spelling)$": { "enum": ["pending", "in_progress", "done"] }
      },
      "minProperties": 1
    },
    "notes": { "type": "string" }
  }
}
```

- [ ] **Step 2: Estendere `tests/check.py` — sezione schema (contenuto esatto)**

In testa ai `# ---- expectations…` aggiungere `import json` accanto a `import re`. Nei registri aggiungere `SCHEMA_PATH`, `FIXTURES_VALID`, `FIXTURES_INVALID`, `PASS_ORDER` e la funzione `check_schema` con invarianti (tra `check_links` e `main`), e una chiamata `check_schema(errors)` dentro `main`:

```python
SCHEMA_PATH = "skills/book-forge/references/meta.schema.json"
FIXTURES_VALID: list[str] = [
    "tests/fixtures/meta-create-intake.json",
    "tests/fixtures/meta-create-chapters.json",
    "tests/fixtures/meta-complete-bible.json",
    "tests/fixtures/meta-revise-passes.json",
    "tests/fixtures/meta-restyle-final-review.json",
    "tests/fixtures/meta-revise-done.json",
]
FIXTURES_INVALID: list[str] = [
    "tests/fixtures/meta-invalid-bad-enum.json",
    "tests/fixtures/meta-invalid-block-size.json",
    "tests/fixtures/meta-invalid-gates.json",
    "tests/fixtures/meta-invalid-file-number.json",
    "tests/fixtures/meta-invalid-flags.json",
    "tests/fixtures/meta-invalid-scope.json",
]
PASS_ORDER = ["structure", "continuity", "style", "grammar", "spelling"]


def check_meta_invariants(meta: dict) -> list[str]:
    """Cross-field rules JSON Schema cannot express. Contract mirrored in
    references/state.md — keep the two in sync."""
    errs: list[str] = []
    phase = meta.get("phase")
    gates = meta.get("gates", {})
    flags = meta.get("flags", {})
    mode = meta.get("work_mode")
    chapters = meta.get("chapters", [])

    # C1 chapter numbering: contiguous ascending from 1, file prefix matches
    numbers = [c.get("number", -1) for c in chapters]
    if numbers != list(range(1, len(numbers) + 1)):
        errs.append("chapters: numbers must be contiguous ascending from 1")
    for c in chapters:
        if not str(c.get("file", "")).startswith(f"manuscript/{c.get('number', 0):02d}-"):
            errs.append(f"chapters: file {c.get('file')!r} does not match number {c.get('number')}")

    # C2 phase-gate coupling — no phase advance without user gates
    if phase in ("chapters", "passes", "final_review", "export", "done") and not gates.get("bible_approved"):
        errs.append("phase beyond 'bible' requires gates.bible_approved")
    if phase in ("final_review", "export", "done") and not gates.get("passes_approved"):
        errs.append("phase beyond 'passes' requires gates.passes_approved")
    if phase in ("export", "done") and not gates.get("final_approved"):
        errs.append("phase beyond 'final_review' requires gates.final_approved")

    # C3 conflicting stop states
    if flags.get("awaiting_fresh_session") and flags.get("degraded_non_independent"):
        errs.append("flags: awaiting_fresh_session and degraded_non_independent are mutually exclusive")

    # C4 web availability must be probed by end of intake
    if phase != "intake" and flags.get("web_available") is None:
        errs.append("flags.web_available must be true/false once past intake")

    # C5 stabilization bookkeeping (work_mode complete only)
    stab = meta.get("stabilization")
    if mode == "complete":
        if not stab:
            errs.append("work_mode 'complete' requires a stabilization block")
        elif phase in ("chapters", "passes", "final_review", "export", "done") and (stab.get("structure") != "done" or stab.get("continuity") != "done"):
            errs.append("mode complete: drafting new chapters requires stabilization done on imported chapters")
    elif stab is not None:
        errs.append("stabilization block is only valid for work_mode 'complete'")

    # C6 pass scope: mode-specific contracts; progress mirrors
    # (create/complete: full macro->micro set; revise: any non-empty subset in
    #  macro->micro order; restyle: exactly [style, continuity, grammar,
    #  spelling] — style/voice first by design, spec W4; the equality checks
    #  pin the order, so the sorted-index check applies to revise subsets only)
    scope = meta.get("pass_scope")
    if scope is not None:
        progress = meta.get("pass_progress")
        if progress is not None and set(progress) != set(scope):
            errs.append("pass_progress keys must mirror pass_scope")
        if not set(scope) <= set(PASS_ORDER):
            errs.append("pass_scope contains unknown passes")
        elif mode == "revise":
            idx = [PASS_ORDER.index(p) for p in scope]
            if idx != sorted(idx):
                errs.append("pass_scope violates macro->micro order: " + " -> ".join(PASS_ORDER))
        elif mode in ("create", "complete"):
            if scope != PASS_ORDER:
                errs.append("work_mode create/complete requires the full pass scope")
        elif mode == "restyle":
            if scope != ["style", "continuity", "grammar", "spelling"]:
                errs.append("work_mode 'restyle' requires pass_scope = style, continuity, grammar, spelling")

    # C7 drafting statuses only during phase 'chapters'; nothing may stay
    # 'planned' (unwritten) once the manuscript is past the chapter cycle
    for c in chapters:
        if c.get("status") in ("drafting", "user_review") and phase != "chapters":
            errs.append(f"chapters: status {c.get('status')!r} valid only in phase 'chapters'")
        if c.get("status") == "planned" and phase in ("passes", "final_review", "export", "done"):
            errs.append("chapters: status 'planned' is not valid beyond phase 'chapters'")

    # C8 imported work must record its chapters — from Gate 1 on: during
    # phase 'bible' (pre-split ingestion) chapters may legitimately be []
    if mode in ("complete", "revise", "restyle") and (phase not in ("intake", "bible") or gates.get("bible_approved")) and not chapters:
        errs.append("imported work_mode with no chapters recorded")

    return errs


def check_schema(errors: list[str]) -> None:
    import jsonschema

    schema_path = ROOT / SCHEMA_PATH
    if not schema_path.is_file():
        errors.append(f"missing file: {SCHEMA_PATH}")
        return
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema)
    for rel in FIXTURES_VALID + FIXTURES_INVALID:
        if not (ROOT / rel).is_file():
            errors.append(f"missing fixture: {rel}")
            continue
        instance = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        schema_errs = [e.message for e in validator.iter_errors(instance)]
        inv_errs = check_meta_invariants(instance)
        if rel in FIXTURES_VALID and (schema_errs or inv_errs):
            errors.extend(f"{rel}: {m}" for m in schema_errs + inv_errs)
        elif rel in FIXTURES_INVALID and not (schema_errs or inv_errs):
            errors.append(f"{rel}: fixture must be INVALID but validates")
```

- [ ] **Step 3: Run per verificare il fallimento atteso**

Run: `uv run tests/check.py`
Expected: `FAIL — 12 problem(s)` — 12 × `missing fixture: tests/fixtures/meta-….json` (lo schema esiste già dallo Step 1: nessun `missing file` atteso).

- [ ] **Step 4: Scrivere le 12 fixture (contenuti esatti)**

`tests/fixtures/meta-create-intake.json`:
```json
{
  "schema_version": 1,
  "project": { "title": "The Lighthouse Road", "slug": "the-lighthouse-road", "language": "en", "created": "2026-11-25" },
  "work_mode": "create",
  "genre_profile": "fiction",
  "validation_mode": { "type": "chapter" },
  "phase": "intake",
  "flags": { "awaiting_fresh_session": false, "degraded_non_independent": false, "web_available": null },
  "gates": { "bible_approved": false, "passes_approved": false, "final_approved": false },
  "chapters": [],
  "continuity_window": 3
}
```

`tests/fixtures/meta-create-chapters.json`:
```json
{
  "schema_version": 1,
  "project": { "title": "The Lighthouse Road", "slug": "the-lighthouse-road", "language": "en", "created": "2026-11-25" },
  "work_mode": "create",
  "genre_profile": "fiction",
  "validation_mode": { "type": "blocks", "block_size": 3 },
  "phase": "chapters",
  "flags": { "awaiting_fresh_session": false, "degraded_non_independent": false, "web_available": false },
  "gates": { "bible_approved": true, "passes_approved": false, "final_approved": false },
  "chapters": [
    { "number": 1, "file": "manuscript/01-the-pact.md", "title": "The Pact", "status": "approved", "origin": "written" },
    { "number": 2, "file": "manuscript/02-the-storm.md", "title": "The Storm", "status": "approved", "origin": "written" },
    { "number": 3, "file": "manuscript/03-the-wreck.md", "title": "The Wreck", "status": "user_review", "origin": "written" }
  ],
  "continuity_window": 3,
  "length_target": { "words": 90000, "chapters": 30 }
}
```

`tests/fixtures/meta-complete-bible.json`:
```json
{
  "schema_version": 1,
  "project": { "title": "Il giardino dei ricordi", "slug": "il-giardino-dei-ricordi", "language": "it", "created": "2026-11-25" },
  "work_mode": "complete",
  "genre_profile": "narrative_nonfiction",
  "validation_mode": { "type": "chapter" },
  "phase": "bible",
  "flags": { "awaiting_fresh_session": false, "degraded_non_independent": false, "web_available": false },
  "gates": { "bible_approved": false, "passes_approved": false, "final_approved": false },
  "chapters": [
    { "number": 1, "file": "manuscript/01-radici.md", "title": "Radici", "status": "imported", "origin": "imported" },
    { "number": 2, "file": "manuscript/02-la-casa-al-mare.md", "title": "La casa al mare", "status": "imported", "origin": "imported" },
    { "number": 3, "file": "manuscript/03-partenze.md", "title": "Partenze", "status": "imported", "origin": "imported" }
  ],
  "continuity_window": 3,
  "stabilization": { "structure": "pending", "continuity": "pending" }
}
```

`tests/fixtures/meta-revise-passes.json`:
```json
{
  "schema_version": 1,
  "project": { "title": "Small Gardens, Deep Roots", "slug": "small-gardens-deep-roots", "language": "en", "created": "2026-11-25" },
  "work_mode": "revise",
  "genre_profile": "practical_nonfiction",
  "validation_mode": { "type": "chapter" },
  "phase": "passes",
  "flags": { "awaiting_fresh_session": false, "degraded_non_independent": false, "web_available": true },
  "gates": { "bible_approved": true, "passes_approved": false, "final_approved": false },
  "chapters": [
    { "number": 1, "file": "manuscript/01-soil.md", "title": "Soil", "status": "imported", "origin": "imported" },
    { "number": 2, "file": "manuscript/02-seeds.md", "title": "Seeds", "status": "imported", "origin": "imported" },
    { "number": 3, "file": "manuscript/03-water.md", "title": "Water", "status": "imported", "origin": "imported" },
    { "number": 4, "file": "manuscript/04-pruning.md", "title": "Pruning", "status": "imported", "origin": "imported" }
  ],
  "continuity_window": 3,
  "pass_scope": ["continuity", "grammar", "spelling"],
  "pass_progress": { "continuity": "done", "grammar": "in_progress", "spelling": "pending" }
}
```

`tests/fixtures/meta-restyle-final-review.json`:
```json
{
  "schema_version": 1,
  "project": { "title": "Cronache di Ghiaccio", "slug": "cronache-di-ghiaccio", "language": "it", "created": "2026-11-25" },
  "work_mode": "restyle",
  "genre_profile": "fiction",
  "validation_mode": { "type": "blocks", "block_size": 5 },
  "phase": "final_review",
  "flags": { "awaiting_fresh_session": true, "degraded_non_independent": false, "web_available": false },
  "gates": { "bible_approved": true, "passes_approved": true, "final_approved": false },
  "chapters": [
    { "number": 1, "file": "manuscript/01-prima-inverno.md", "title": "Prima dell'inverno", "status": "imported", "origin": "imported" },
    { "number": 2, "file": "manuscript/02-la-caccia.md", "title": "La caccia", "status": "imported", "origin": "imported" },
    { "number": 3, "file": "manuscript/03-il-patto.md", "title": "Il patto", "status": "imported", "origin": "imported" },
    { "number": 4, "file": "manuscript/04-il-thaw.md", "title": "Il thaw", "status": "imported", "origin": "imported" },
    { "number": 5, "file": "manuscript/05-dopo.md", "title": "Dopo", "status": "imported", "origin": "imported" }
  ],
  "continuity_window": 4,
  "pass_scope": ["style", "continuity", "grammar", "spelling"],
  "pass_progress": { "style": "done", "continuity": "done", "grammar": "done", "spelling": "done" }
}
```

`tests/fixtures/meta-revise-done.json`:
```json
{
  "schema_version": 1,
  "project": { "title": "Small Gardens, Deep Roots", "slug": "small-gardens-deep-roots", "language": "en", "created": "2026-11-25" },
  "work_mode": "revise",
  "genre_profile": "practical_nonfiction",
  "validation_mode": { "type": "chapter" },
  "phase": "done",
  "flags": { "awaiting_fresh_session": false, "degraded_non_independent": true, "web_available": true },
  "gates": { "bible_approved": true, "passes_approved": true, "final_approved": true },
  "chapters": [
    { "number": 1, "file": "manuscript/01-soil.md", "title": "Soil", "status": "imported", "origin": "imported" },
    { "number": 2, "file": "manuscript/02-seeds.md", "title": "Seeds", "status": "imported", "origin": "imported" },
    { "number": 3, "file": "manuscript/03-water.md", "title": "Water", "status": "imported", "origin": "imported" },
    { "number": 4, "file": "manuscript/04-pruning.md", "title": "Pruning", "status": "imported", "origin": "imported" }
  ],
  "continuity_window": 3,
  "pass_scope": ["continuity", "grammar", "spelling"],
  "pass_progress": { "continuity": "done", "grammar": "done", "spelling": "done" },
  "notes": "self-review override: fresh-session unavailable, user accepted degraded_final_review"
}
```

`tests/fixtures/meta-invalid-bad-enum.json`:
```json
{
  "schema_version": 1,
  "project": { "title": "X", "slug": "x", "language": "en", "created": "2026-11-25" },
  "work_mode": "create",
  "genre_profile": "fiction",
  "validation_mode": { "type": "chapter" },
  "phase": "drafting",
  "flags": { "awaiting_fresh_session": false, "degraded_non_independent": false, "web_available": false },
  "gates": { "bible_approved": false, "passes_approved": false, "final_approved": false },
  "chapters": [],
  "continuity_window": 3
}
```

(`web_available` va tenuto `false` in questa notazione: con `phase` fuori enum scatta SOLO l'errore di enum dello schema — motivo esclusivo, vedi Amendamento 2.)

`tests/fixtures/meta-invalid-block-size.json`: come `meta-create-intake.json` ma `"validation_mode": { "type": "blocks", "block_size": 1 }`.

`tests/fixtures/meta-invalid-gates.json`: come `meta-revise-passes.json` ma `"gates": { "bible_approved": false, "passes_approved": false, "final_approved": false }` (phase `passes` senza bibbia approvata → invariante C2).

`tests/fixtures/meta-invalid-file-number.json`: come `meta-complete-bible.json` ma il capitolo 2 ha `"file": "manuscript/03-echoes.md"` (→ invariante C1).

`tests/fixtures/meta-invalid-flags.json`: come `meta-restyle-final-review.json` ma `"flags": { "awaiting_fresh_session": true, "degraded_non_independent": true, "web_available": false }` (→ C3).

`tests/fixtures/meta-invalid-scope.json`: come `meta-restyle-final-review.json` ma `"pass_scope": ["style", "spelling"]` e `pass_progress` coerente con quel set (→ C6: scope restyle incompleto).

- [ ] **Step 5: Run per verificare che passi**

Run: `uv run tests/check.py`
Expected: `OK — all checks passed` — le 6 fixture valide passano schema + invarianti; le 6 invalide sono rifiutate ciascuna per il motivo giusto (2 via schema, 4 via invarianti).

- [ ] **Step 6: Scrivere `skills/book-forge/references/state.md`**

Registro: `REQUIRED_FILES` += `skills/book-forge/references/state.md`; `REQUIRED_HEADERS` =
```python
[
    "## meta.json — fields",
    "## Transition rules",
    "## Project directory layout",
    "## Naming and language rules",
    "## Resuming a project",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "written only by the orchestrator",
    "references/<phase>.md",
    "continuity_window",
    "meta.schema.json",
]
```
Run → FAIL (file mancante), poi scrivere il file:

- `## meta.json — fields`: tabella campo → tipo/valori → chi lo scrive → quando (i campi/enum dell'Interfaccia di questo task, in copia conforme a `meta.schema.json`, citato come autorità macchina). Notare il default `continuity_window: 3` (range 2–10).
- `## Transition rules`: elenco numerato: (1) `meta.json` is written only by the orchestrator — subagenti mai; (2) avanzamenti di fase SOLO con i gate della invariante C2 (bible_approved prima di chapters/passes; passes_approved prima di final_review; final_approved prima di export); (3) `awaiting_fresh_session=true` blocca TUTTO finché la pipeline non riprende in una sessione NUOVA: la sessione nuova si riconosce fresca = nessun turno di stesura/editing di questo libro nel proprio contesto, e solo allora esegue `awaiting_fresh_session: false` e avvia la review; in inline, con libri lunghi, i dispatch di review si possono frazionare in più sessioni fresche consecutive (override utente esplicito → `degraded_non_independent: true`, mai entrambi i flag — C3); (4) web_available va stabilito a fine intake; (5) capitolo: `planned|imported→drafting→user_review→(correzioni→drafting)→approved`; status `drafting|user_review` solo in phase `chapters`; status `planned` vietato da `passes` in poi (capitolo mai scritto — C7); (6) work_mode complete: stabilization (structure+continuity su 1..M) `done` OBBLIGATORIO prima di chapters e non può più retrocedere: resta `done` in tutte le fasi successive (C5); (7) pass_scope/pass_progress vincolati per modalità (C6): create/complete = tutte e cinque in ordine macro→micro; revise = sottoinsieme non vuoto in ordine macro→micro fissato dal revision-plan al Gate 1; restyle = esattamente [style, continuity, grammar, spelling] (voce prima per design, W4); (8) dopo l'impostazione di un campo di gate, non si retrocede mai senza decisione utente esplicita; unica retrocessione controllata prevista: capitolo bocciato al gate finale → conferma utente esplicita → `phase: "passes"` + `gates.passes_approved: false` → passata mirata sul capitolo + `resync facts-index` → nuovo Gate (b) → nuovo ingresso in `final_review` (in inline `awaiting_fresh_session` torna `true`: la sessione ormai ha editato prosa); (9) `<phase>` nella regola di resume si risolve SEMPRE via tabella phase × work_mode (mai nome file letterale: `final_review` → `final-review.md`): intake→`references/intake.md`; bible→`references/bible.md` (create) | `references/ingest.md` (esistenti con `chapters == []`) | `references/reconstruction.md` (esistenti con capitoli importati); chapters→`references/drafting.md`; passes→`references/passes.md`; final_review→`references/final-review.md`; export/done→`references/export.md`.
- `## Project directory layout`: l'albero del progetto utente riportato in questo piano (verbatim).
- `## Naming and language rules`: `manuscript/NN-slug.md` (NN 2 cifre), primo heading `# <titolo>`, slug kebab **ASCII** — i titoli con accenti o alfabeti non latini si translitterano (fallback `chapter-NN` quando la translitterazione non è affidabile); prosa degli artefatti di progetto nella lingua del libro; chiavi/file della skill in inglese.
- `## Resuming a project`: regola W1: leggi `meta.json` → `references/state.md` → rileggi `references/<phase>.md` a ogni sessione.

- [ ] **Step 7: Run finale del task e commit**

Run: `uv run tests/check.py` → Expected: `OK`. Commit:

```bash
git add skills/book-forge/references/meta.schema.json skills/book-forge/references/state.md tests/
git commit -m "feat(skill): meta.json schema, state reference, fixtures (W1 resume, gate coupling)"
```

### Task 5: references/intake.md — fase 0

**Files:**
- Create: `skills/book-forge/references/intake.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: campi/enum `meta.json` del Task 4 (li scrive a fine colloquio: `work_mode`, `genre_profile`, `validation_mode`, `project`, `flags.web_available`, `phase: "bible"`).
- Produces: protocollo colloquio + convenzioni `research/` + logica auto-rivelazione dei 4 lavori (consumata da SKILL.md e drafting/reconstruction).

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `skills/book-forge/references/intake.md`; `REQUIRED_HEADERS` =
```python
[
    "## Protocol",
    "## Step 1 — identify the job",
    "## Step 2 — validation mode (ask first)",
    "## Core questions (all profiles)",
    "## Question topics — fiction",
    "## Question topics — practical nonfiction",
    "## Question topics — narrative nonfiction",
    "## Raw material",
    "## Online research",
    "## Write meta.json",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "one question at a time",
    "in the user's own language",
    "create | complete | revise | restyle",
    "validation_mode",
    "web_available",
]
```

- [ ] **Step 2: Run → Expected: FAIL (`missing file: skills/book-forge/references/intake.md`)**

- [ ] **Step 3: Scrivere `intake.md`**, espandendo per spec (obiettivi 1–2, 4; builder-check 7; decisione utente 1–2):

- `## Protocol`: una domanda alla volta; nella lingua dell'utente (`in the user's own language`) senza gergo editoriale (o col gergo spiegato); registrare le risposte; non chiedere mai in un colpo solo; il question bank è questo file (artefatto inglese, conversazione localizzata).
- `## Step 1 — identify the job`: come si auto-rivela il lavoro: nessun manoscritto esistente → `create`; manoscritto parziale con capitoli esistenti → `complete`; libro finito/da sistemare → `revise`; libro finito ma nuova voce richiesta → `restyle`. Domanda di disambiguazione se l'utente fornisce file ma non dice cosa vuole (le 3 alternative con parole povere). Esito = `work_mode` ∈ `create | complete | revise | restyle` (stringa pinnata).
- `## Step 2 — validation mode (ask first)`: DOMANDA OBBLIGATORIA iniziale: un capitolo alla volta (default, `chapter`) oppure blocchi di N (`blocks`, `block_size` N≥2, gate umano ogni N capitoli). Registro in `validation_mode`.
- `## Core questions (all profiles)`: profilo genere (`fiction | practical_nonfiction | narrative_nonfiction`), audience, promessa centrale, tono/voce, lingua del libro (`project.language`, BCP-47), lunghezza target (`length_target`).
- `## Question topics — fiction`: premise in una frase; protagonista/i e desiderio; mondo/ambientazione; POV; arco temporale; cuore emotivo (cosa conta davvero); epilogo noto o da scoprire; tabù di contenuto.
- `## Question topics — practical nonfiction`: la trasformazione del lettore (da cosa a cosa); prerequisiti del lettore; promesse per parte del libro; esercizi/esempi desiderati; registro del tono (diretto/empatico).
- `## Question topics — narrative nonfiction`: la timeline di ciò che è accaduto davvero; le persone reali e le sensibilità/riservatezza; il tema (di cosa parla, sotto la superficie); quantità di tessuto narrativo vs nudo resoconto.
- `## Raw material`: appunti/file/concetti forniti dall'utente → `research/`; se presenti, il colloquio parte da lì e accorcia le domande; `research/sources.md` per ogni fonte (URL + access date) quando online.
- `## Online research`: solo su richiesta esplicita; se l'ambiente non offre accesso web, il Researcher dichiara subito il limite e lavora sul solo materiale utente (eccezione protetta 2); esito del probe → `flags.web_available` (false→null check C4).
- `## Write meta.json`: alla fine: crea il progetto (`<project-dir>` scelto con l'utente), inizializza albero (solo dir servite), scrive `meta.json` con i campi del Task 4, `phase: "bible"`, `chapters: []` (in OGNI work_mode: per i lavori su esistente i capitoli arrivano dall'ingestione e fino allo split confermato restano `[]` — stato tollerato da C8 fino al Gate 1); per i lavori su esistente si prosegue su `references/ingest.md`; lo scrive l'orchestratore, non un subagente.

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/intake.md tests/check.py
git commit -m "feat(skill): intake interview protocol (phase 0, mode auto-reveal)"
```

### Task 6: references/ingest.md — ingestione W2

**Files:**
- Create: `skills/book-forge/references/ingest.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: Task 4 (capitoli `origin: "imported"`, `status: "imported"`; naming `manuscript/NN-slug.md`).
- Produces: adapter ingestione (pandoc .docx primario; estrattore dedicato per .pdf) + protocollo conferma split. Consumato da `reconstruction.md` (Task 9).

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `skills/book-forge/references/ingest.md`; `REQUIRED_HEADERS` =
```python
[
    "## Formats and adapters",
    "## Convert .docx",
    "## Convert .pdf",
    "## Propose the chapter split",
    "## Write the chapter files",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "pandoc cannot read PDF",
    "user confirms the chapter split",
    "heading search or line ranges",
    "--from docx --to gfm --wrap=none",
    "declare the limitation",
    "never edit the prose",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancante)**

- [ ] **Step 3: Scrivere `ingest.md`** (spec: Vincoli; W2; builder-check 2, 11):

- `## Formats and adapters`: .docx → pandoc (primario, fallback qualunque convertitore offerto dall'ambiente); .pdf → **estrattore di testo dedicato** perché `pandoc cannot read PDF` come INPUT (pandoc fa solo output PDF): candidati in ordine — `pdftotext`, convertitori dell'ambiente, python lib se disponibili; se nulla è disponibile: declare the limitation esplicitamente e chiedere all'utente un'alternativa (esporta in .docx/txt). I capitoli creati si registrano con `origin: "imported"`.
- `## Convert .docx`: comando esatto: `pandoc --from docx --to gfm --wrap=none --output research/manuscript-raw.md <input.docx>`; poi normalizzazione leggera (heading level coerenti) SENZA toccare la prosa: `never edit the prose` — l'ingestione non emenda mai il testo.
- `## Convert .pdf`: pipeline estrattore → markdown grezzo → stessa disciplina; nota che immagini/layout andranno persi e va dichiarato.
- `## Propose the chapter split`: euristiche sui confini (heading search su livello 1/2, pattern "Chapter N", salti di pagina) operate per **heading search or line ranges** (grep/slicing con script leggero) — MAI leggendo `research/manuscript-raw.md` per intero in un contesto LLM (economia di contesto cardinale); proponi la lista numerata dei confini (titolo proposto + prima riga + n. parole — contato meccanicamente); il loop si chiude SOLO quando `user confirms the chapter split` (W2) — la conferma dell'utente è obbligatoria prima di scrivere i file.
- `## Write the chapter files`: scrivi `manuscript/NN-slug.md` (NN 2 cifre, slug kebab **ASCII**: translitterazione del titolo; fallback `chapter-NN` per alfabeti non latini — vedi Naming rules di state.md), ciascuno con `# <titolo>` come primo heading; registra i capitoli in `meta.json` (`status: "imported"`, `origin: "imported"`) — orchestratore only; poi `phase` resta `bible` e il seguito è `references/reconstruction.md`.

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/ingest.md tests/check.py
git commit -m "feat(skill): manuscript ingestion adapters (W2: docx/pandoc, pdf/extractor, user-confirmed split)"
```

### Task 7: references/bible.md — fase 1 creazione

**Files:**
- Create: `skills/book-forge/references/bible.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: Task 4 (`gates.bible_approved`, `phase: "chapters"`), Task 5 (uscita intake), ruolo `researcher.md` del Task 9 (path citata: `references/roles/researcher.md` — a questo task NON ancora esistente: citarla come inline code pura, NON come hyperlink, così il link-check non fallisce).
- Produces: template bibbia ×3 profili + formato outline + euristica lunghezza; consumati da drafting (Task 10) e reconstruction (Task 9).

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `skills/book-forge/references/bible.md`; `REQUIRED_HEADERS` =
```python
[
    "## Who works and how",
    "## bible.md — fiction template",
    "## bible.md — practical nonfiction template",
    "## bible.md — narrative nonfiction template",
    "## Style guide",
    "## outline.md format",
    "## Chapter length heuristic",
    "## Gate 1 — approve the bible",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "references/roles/researcher.md",
    "references/ingest.md",
    "references/reconstruction.md",
    "2,000–4,000",
    "3,000–5,000",
    "2,500–4,500",
    "[min]",
    "[opt]",
    "gates.bible_approved",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancante)**

- [ ] **Step 3: Scrivere `bible.md`** (spec: obiettivo 3; profili genere; builder backlog):

- `## Who works and how` (CREATION TRACK — prima riga del file: «This file is the creation track. If `work_mode` is not `create`, do not use it alone: with no chapters yet read `references/ingest.md`; with imported chapters read `references/reconstruction.md`.»): dispatch del Researcher (`references/roles/researcher.md`) con input: trascrizione colloquio + `research/`; produce draft di `bible.md` + `outline.md`; l'orchestratore li presenta; NIENTE canon non validato prima del Gate 1 (la bibbia è contratto, non sbozzato).
- `## bible.md — fiction template` — campi [min]: Premise (una frase + paragrafo), Characters (nome, want, need, arc, stato iniziale), World (luoghi, regole), POV, Tone; campi [opt]: Archi secondari, Timeline, Convenzioni di genere (che pay-off il lettore si aspetta).
- `## bible.md — practical nonfiction template` — [min]: Transformation (da cosa a cosa), Audience, Core concepts (elenco), Reader promises (cosa sa fare il lettore a fine di ogni parte), TOC logic; [opt]: Prerequisiti, Glossario di dominio, Case study disponibili.
- `## bible.md — narrative nonfiction template` — [min]: True spine (timeline di ciò che è accaduto), Cast reale, Theme, Sensibilità/riservatezza; [opt]: Tessuto narrativo concesso, Fonti.
- `## Style guide`: sezione OBBLIGATORIA della bibbia in tutti i profili: voce normativa (come deve suonare), registro, persona, tempi, tabù lessicali; esempi few-shot brevi. Nota: questa è la style guide NORMATIVA (creazione); quella descrittiva appartiene a reconstruction (Task 9).
- `## outline.md format`: per ogni capitolo: `## 01 — <title>` + blocchi: Purpose (perché esiste nel libro), Contract (cosa promette/risolve), Beats (fiction: 3–7 beat; nonfiction: key points + esercizio/eventuale), Continuity hooks (da quali fatti dipende), Target range (dall'euristica sotto); la TOC segue i template di cui sopra.
- `## Chapter length heuristic` (tabella pinnata, default modificabili dall'utente):

| Profile | Chapter length (words) | Default book target (words) |
|---|---|---|
| fiction | 2,000–4,000 | 80,000–90,000 |
| practical_nonfiction | 3,000–5,000 | 40,000–60,000 |
| narrative_nonfiction | 2,500–4,500 | 55,000–75,000 |

  Derivazione: capitoli ≈ `length_target.words` / centro del range capitolo (arrotondato); l'introduzione di un manuale è tipicamente più corta (1,500–2,500 parole).
- `## Gate 1 — approve the bible`: presenta bibbia+outline all'utente; l'utente modifica/approva; SOLO all'approvazione l'orchestratore: (a) inizializza `meta.json.chapters` da `outline.md` — 1..N, `status: "planned"`, `origin: "written"` (mode create); (b) setta `gates.bible_approved: true` e `phase: "chapters"`. Mai auto-approvare; se l'utente vuole ricerche aggiuntive, torna al Researcher.

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/bible.md tests/check.py
git commit -m "feat(skill): bible & outline templates per genre + chapter length heuristic"
```

### Task 8: references/ledger.md — facts-index + window

**Files:**
- Create: `skills/book-forge/references/ledger.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: Task 4 (`continuity_window` = K).
- Produces: formato `continuity/facts-index.md` (tabella 6 colonne), formato handoff `continuity/window/NN-*.md`, protocollo di aggiornamento post-approvazione. Consumato da: drafting (Task 10), reconstruction (Task 9), passes/continuity (Task 11), final-review (Task 13).

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `skills/book-forge/references/ledger.md`; `REQUIRED_HEADERS` =
```python
[
    "## facts-index.md",
    "## Handoff window",
    "## Update after each approved chapter",
    "## Change discipline",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "| ID | Type | Fact or statement | Established | Source | Status |",
    "[ch.NN]",
    "superseded",
    "the last K approved chapters",
    "never mutate the index before a user decision",
    "PROVISIONAL",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancante)**

- [ ] **Step 3: Scrivere `ledger.md`** (spec: B2; obiettivo 8; formato continuity/):

- `## facts-index.md`: tabella con colonne esatte `| ID | Type | Fact or statement | Established | Source | Status |`: Type ∈ `character, place, object, event, timeline, promise, term, thread` (thread = foreshadowing/vincoli aperti); Established = provenienza del tipo `[ch.NN]` (o `bible §section` per fatti canonici); Source = file bibbia o capitolo; Status ∈ `canon | superseded | provisional` — `provisional` SOLO durante lo sweep diagnostico (Task 9), prima della bibbia validata. Regola: mai cancellare una riga: la versione confutata è marcata `superseded` con la riga nuova accanto.
- `## Handoff window`: `continuity/window/NN-slug.md`, uno per capitolo APPROVATO, lunghezza massima ~30 righe: What happened (3–6 bullet), New facts (ID aggiunti), Open threads (ancora da pagare), Character states (stato alla fine del capitolo), Voice notes. La finestra contiene the last K approved chapters (K = `continuity_window`): i file oltre K si ELIMINANO (i fatti vivono nell'index, la window è solo contesto di handoff). CICLO DI VITA: la window della fase 2 resta CONGELATA a fine ciclo capitoli; ogni passata sequenziale della fase 3 la RICOSTRUISCE come finestra scorrevole della passata in corso (Task 11); sugli importati la popola lo sweep (Task 9).
- `## Update after each approved chapter`: dispatch del Continuity-checker (`references/roles/continuity-checker.md` — task 12, citare come inline code, no hyperlink): input = capitolo approvato + window corrente + facts-index; output = righe nuove/aggiornate dell'index + nuovo handoff file + pruning a K. L'orchestratore scrive solo meta.json.
- `## Change discipline`: `never mutate the index before a user decision`: le righe si aggiungono da capitoli approvati o bibbia validata; ogni rettifica suggestionata fuori da questi canali → STOP → protocollo contraddizioni di `passes.md`. Unica eccezione dichiarata: lo sweep diagnostico (Task 9) POPOLA l'index con righe PROVISIONAL prima del Gate 1 (Status = `provisional`); la canonizzazione in `canon`/`superseded` avviene SOLO con la bibbia validata dall'utente al Gate 1 — la decisione resta sempre dell'utente.

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/ledger.md tests/check.py
git commit -m "feat(skill): continuity ledger — facts-index with provenance + K-window handoff (B2)"
```

### Task 9: references/reconstruction.md + roles/researcher.md

**Files:**
- Create: `skills/book-forge/references/reconstruction.md`, `skills/book-forge/references/roles/researcher.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: Task 6 (ingest → capitoli `imported`), Task 7 (template bibbia — qui usati come schema della bibbia RICOSTRUITA), Task 8 (facts-index/window), Task 4 (`work_mode`, `stabilization`, `pass_scope` per restyle).
- Produces: percorso fase 1 per modes complete/revise/restyle: sweep diagnostico per capitolo, bibbia ricostruita con style guide DESCRITTIVA, revision-plan (revise), pilot.md (restyle), subset stabilizzazione (complete). Ruolo Researcher (duty A già usato da Task 7; duty B qui).

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `["skills/book-forge/references/reconstruction.md", "skills/book-forge/references/roles/researcher.md"]`;

`REQUIRED_HEADERS["skills/book-forge/references/reconstruction.md"]` =
```python
[
    "## When this track runs",
    "## Diagnostic sweep",
    "## The rebuilt bible",
    "## Mode complete — Gate 1 and stabilization",
    "## Mode revise — Gate 1 and the revision plan",
    "## Mode restyle — new voice and the pilot",
]
```
`REQUIRED_HEADERS["skills/book-forge/references/roles/researcher.md"]` =
```python
[
    "## Identity",
    "## Duty A — compile the bible (mode create)",
    "## Duty B — reconstruct (modes complete / revise / restyle)",
    "## Copyright discipline",
    "## Output contract",
    "## Never",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/reconstruction.md"]` =
```python
[
    "descriptive style guide",
    "one chapter per dispatch",
    "structure and continuity",
    "revision-plan.md",
    "pilot.md",
    "the old book releases only canon, facts and ledger",
    "research/reconstruction-notes.md",
    "outline.md",
    "status: \"planned\"",
    "references/roles/copy-editor.md",
    "normative",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/roles/researcher.md"]` =
```python
[
    "declare it immediately",
    "source URL and the access date",
    "do not write meta.json",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancanti ×2)**

- [ ] **Step 3: Scrivere `reconstruction.md`** (spec: obiettivi 1(ii-iv), 3; matrice; B3; W4):

- `## When this track runs`: modes complete/revise/restyle con capitoli `imported` (dopo ingest); per mode bible re-read rule; rimanda il lavoro (i) a `bible.md`.
- `## Diagnostic sweep`: per OGNI capitolo importato, un subagent fresco (Researcher, duty B) — `one chapter per dispatch`, in sequenza (mai il libro intero): input di OGNI dispatch = capitolo corrente + `continuity/facts-index.md` provisionale cumulativo + `research/reconstruction-notes.md` (note estratte dei capitoli precedenti); estrae canon (personaggi/mondo/concetti), glossario, righe PROVISIONAL di facts-index con provenienza, osservazioni di stile (frasi campione), sintesi purpose/beat del capitolo (per assemblare `outline.md`) e handoff window, e CONTRADDIZIONI mano a mano che emergono (con provenienza `[ch.NN]` di entrambe le versioni — formato del Task 8): così il capitolo 12 vede i fatti del capitolo 04 senza mai caricare i capitoli precedenti. Le contraddizioni si registrano, NON si risolvono nello sweep.
- `## The rebuilt bible`: assemblaggio (orchestratore/Researcher) in `bible.md` con template del Task 7 leggendo SOLO le `research/reconstruction-notes.md` (mai rileggendo i capitoli), MA la style guide qui è descrittiva: `descriptive style guide` — come suona il libro ORA (con estratti reali come few-shot), NON normative; avviso esplicito che la normative nasce dal Gate 1. INSIEME alla bibbia si assemblano: `outline.md` sui capitoli importati 1..M (dalle sintesi purpose/beat dello sweep) e `continuity/window/` con gli handoff degli ULTIMI K capitoli importati.
- `## Mode complete — Gate 1 and stabilization`: l'utente valida la bibbia ricostruita — con la validazione la style guide descrittiva diventa NORMATIVA (l'utente accetta la voce attuale o indica dove il libro NON è quello che voleva — spec obiettivo 3) — e approva `outline.md`: i contratti dei capitoli esistenti 1..M E i contratti dei NUOVI capitoli M+1..N (il TOC mancante si integra col colloquio, Task 5); poi STABILIZZAZIONE obbligatoria dei capitoli importati 1..M prima di scrivere il primo capitolo nuovo: SOLO le passate `structure and continuity` SU 1..M (motore di `passes.md`, task 11 — W4), macro→micro; style/grammar/spelling restano alla fase 3 sull'intero libro; conclusa la stabilizzazione: l'orchestratore registra i capitoli M+1..N in `meta.json.chapters` (`status: "planned"`, `origin: "written"`), `stabilization` → entrambi `done`, e SOLO ALLORA `phase: "chapters"` (invarianti C5/C7).
- `## Mode revise — Gate 1 and the revision plan`: Gate 1 = l'utente valida la bibbia ricostruita ("è il libro che hai scritto?" — con la validazione la style guide descrittiva diventa NORMATIVA) + approva `outline.md` ricostruito e `revision-plan.md`: formato pinnato — per passata selezionata: scopo + per-capitolo note (dove intervenire e perché) + cosa NON toccare; `pass_scope` si deriva dal piano approvato (sottoinsieme, ordine macro→micro); poi `phase: "passes"` (qui i capitoli sono già tutti `status: "imported"` — nessuno `planned`, C7). (Spec: "la style guide normativa nasce dalla validazione dell'utente al Gate 1 — l'utente può accettare la voce attuale o dire dove il libro NON è quello che voleva".)
- `## Mode restyle — new voice and the pilot`: colloquio (intake) per la NUOVA voce → style guide NORMATIVA nella bibbia; vincolo della spec: `the old book releases only canon, facts and ledger` — la vecchia style guide NON entra MAI; il pilota = 1 capitolo (o estratto lungo) riscritto nella nuova voce da un dispatch di `references/roles/copy-editor.md` (passata style/voice; input: solo il capitolo scelto + nuova style guide + canon/fatti del ledger estratti) con round-trip finché l'utente lo approva al Gate 1 → salvato in `pilot.md` come ancora few-shot di OGNI dispatch di passata stile; `pass_scope` = [style, continuity, grammar, spelling] (C6); poi `phase: "passes"` (come revise: nessun capitolo `planned`).

- [ ] **Step 4: Scrivere `roles/researcher.md`**:

- `## Identity`: "You are the Researcher. You compile and reconstruct — you never draft chapters and never edit prose." (harness-agnostic, nessun nome di tool).
- `## Duty A — compile the bible (mode create)`: da trascrizione colloquio + `research/` → bozza `bible.md` + `outline.md` (template Task 7); ricerca online SOLO se richiesta dall'utente e possibile; le lacune non si colmano con invenzioni: tornano al colloquio come domande da porre (una per volta).
- `## Duty B — reconstruct (modes complete / revise / restyle)`: per UN capitolo per volta (sequenziale, contesto fresco; input: capitolo + facts-index provisionale cumulativo + `research/reconstruction-notes.md`): estrazione canon/facts/glossario/style observations/contraddizioni + sintesi purpose/beat per `outline.md` + handoff window del capitolo (formati dei Task 7–8); aggiorna note e righe PROVISIONAL dell'index; no judgement, no fix; le contraddizioni riportate CON provenienza.
- `## Copyright discipline`: ogni testo riportato porta la fonte: `source URL and the access date` in `research/sources.md`; riscrittura con parole proprie SOLO su richiesta esplicita dell'utente, e comunque la fonte resta tracciata.
- `## Output contract`: file prodotti (bozze, estratti, righe di facts-index pronte da inserire, contraddizioni documentate); formato risposta breve all'orchestratore.
- `## Never`: `do not write meta.json`; non scrivere in `manuscript/`; non risolvere contraddizioni da solo; non emendare prosa altrui; se non puoi cercare online, `declare it immediately` e prosegui sul materiale utente dichiarando il limite nell'output.

- [ ] **Step 5: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/reconstruction.md skills/book-forge/references/roles/researcher.md tests/check.py
git commit -m "feat(skill): reconstruction track for existing manuscripts + researcher role (B3, W4)"
```

### Task 10: references/drafting.md + roles/drafter.md — fase 2

**Files:**
- Create: `skills/book-forge/references/drafting.md`, `skills/book-forge/references/roles/drafter.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: Task 4 (`validation_mode`, status capitolo), Task 5 (blocks), Task 7 (contratto capitolo in outline), Task 8 (window + facts-index), Task 9 (mode complete: stabilization done).
- Produces: ciclo capitolo a gate umano con round-trip del DRAFTER + ruolo drafter; consumato da SKILL.md.

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `["skills/book-forge/references/drafting.md", "skills/book-forge/references/roles/drafter.md"]`;

`REQUIRED_HEADERS["skills/book-forge/references/drafting.md"]` =
```python
[
    "## The chapter cycle",
    "## Dispatching the drafter",
    "## User review and immediate rewrite",
    "## Closing a chapter",
    "## Blocks of N",
    "## Never",
]
```
`REQUIRED_HEADERS["skills/book-forge/references/roles/drafter.md"]` =
```python
[
    "## Identity",
    "## Inputs",
    "## Routine",
    "## Output contract",
    "## Never",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/drafting.md"]` =
```python
[
    "the same drafter",
    "stateless",
    "only after the user approves the current chapter",
    "status: user_review",
    "pass_scope",
    "continuity/window/",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/roles/drafter.md"]` =
```python
[
    "do not write meta.json",
    "never edit approved chapters",
    "bible.md",
    "one chapter",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancanti ×2)**

- [ ] **Step 3: Scrivere `drafting.md`** (spec: obiettivo 6; decisioni utente 2–3; builder-check 8):

- `## The chapter cycle`: ciclo di un capitolo con le stringhe di stato esatte del registro (`status: drafting`, `status: user_review`, `status: approved`): pick del prossimo `planned` → `status: drafting` → dispatch DRAFTER → `status: user_review` → l'utente legge → correzioni → stesso DRAFTER (round-trip) → nuova lettura → `status: approved`. Il capitolo si chiude SOLO all'approvazione.
- `## Dispatching the drafter`: input del prompt: role path + `bible.md` + contratto del capitolo (da `outline.md`) + window (`continuity/window/`) + righe di facts-index citate dal contratto; MAI altri capitoli interi; il draft si scrive in `manuscript/NN-slug.md`; lingua = `project.language`; target range dall'euristica.
- `## User review and immediate rewrite`: presentare il capitolo; le correzioni dell'utente tornano VERBATIM a `the same drafter` che riscrive IMMEDIATAMENTE (round-trip; l'orchestratore orchestra soltanto, non emenda); se l'harness ha subagent one-shot stateless, "the same drafter" = ri-dispatch del ruolo Drafter col draft corrente del capitolo + correzioni verbatim + bibbia + contratto + window (la continuità vive nei file di progetto, non nell'identità dell'istanza); poi nuova lettura; le correzioni NON si accumulano a fine lavorazione (decisione utente 3).
- `## Closing a chapter`: `approved` → dispatch Continuity-checker per ledger+window (Task 8) → advances `only after the user approves the current chapter`; nessuna stesura oltre il gate (status `user_review` registrato con `status: user_review`). Quando l'ULTIMO capitolo pianificato diventa `approved`: l'orchestratore setta `phase: "passes"` e inizializza `pass_scope`/`pass_progress` secondo C6 (create/complete: tutte e cinque; revise/restyle: come fissato al Gate 1).
- `## Blocks of N`: `validation_mode.type == "blocks"`: si scrivono N capitoli di fila (uno per dispatch, sempre con handoff aggiornato), poi UNA sola sessione di lettura per il blocco; correzioni → round-trip sui capitoli del blocco; approvato il blocco → tutti `approved` → ledger update; MAI scrivere oltre il blocco in attesa.
- `## Never`: non procedere oltre il gate; non aggiornare la bibbia durante la stesura (le deviazioni diventano domande per l'utente); non lasciare status `drafting`/`user_review` a fine sessione senza dirlo all'utente.

- [ ] **Step 4: Scrivere `roles/drafter.md`**:

- `## Identity`: "You are the Drafter. You write new chapters to contract — you are the only one who edits a chapter's prose during the chapter cycle."
- `## Inputs`: bibbia (full), contratto capitolo, window handoff, righe facts-index; descrizione di cosa guardare per continuità.
- `## Routine`: leggere gli input; scrivere il capitolo IN LINGUA LIBRO rispettando voce/contratto/beat; rispettare i fatti dell'index; novità non previste dal contratto → segnalarle all'orchestratore NON inventarle come canon; `one chapter` per dispatch.
- `## Output contract`: file capitolo aggiornato + nota breve (cosa instaurato che il ledger deve registrare: nuovi fatti/thread).
- `## Never`: `never edit approved chapters`; `do not write meta.json`; non scrivere bibbia/ledger/facts-index (solo segnalarli); non copiare testo di fonti (copyright discipline).

- [ ] **Step 5: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/drafting.md skills/book-forge/references/roles/drafter.md tests/check.py
git commit -m "feat(skill): chapter drafting cycle with human gate round-trip + drafter role"
```

### Task 11: references/passes.md — fase 3, il motore di correzione

**Files:**
- Create: `skills/book-forge/references/passes.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: Task 4 (`pass_scope`, `pass_progress`, invariante C6), Task 7 (style guide + pilot per restyle), Task 8 (facts-index/window), ruoli Task 12 (citati come inline code path), Task 9 (revision-plan / stabilizzazione / pilot come ancora).
- Produces: ordine e routine delle passate, protocollo contraddizioni, resync (W5), formato registri, gate protocol (b). Consumato da reconstruction (stabilizzazione) e SKILL.md.

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `skills/book-forge/references/passes.md`; `REQUIRED_HEADERS` =
```python
[
    "## Pass order and per-mode scope",
    "## How each pass runs",
    "## Contradiction protocol",
    "## facts-index resync",
    "## Diff registries",
    "## Gate — protocol (b)",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "structure → continuity → style/voice → grammar → spelling",
    "style/voice → continuity → grammar → spelling",
    "one chapter per dispatch",
    "only the chapters in error",
    "stop and ask the user",
    "resync facts-index",
    "passes/registry-",
    "macro to micro",
    "aggregated by the orchestrator",
    "passes/registry-<pass>/ch-NN.md",
    "sliding window",
    "stabilization (phase 1)",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancante)**

- [ ] **Step 3: Scrivere `passes.md`** (spec: obiettivi 7–8; B1, B2; decisioni utente 9–12; W4, W5; matrix):

- `## Pass order and per-mode scope`: ordine fisso `macro to micro`: stringa esatta `structure → continuity → style/voice → grammar → spelling` — ogni passata che riscrive prosa passa PRIMA delle micro correzioni, così la prosa riscritta arriva comunque verificata a valle (B1). Scope per modalità (W4): create/complete = tutte; revise = sottoinsieme da `revision-plan.md` approvato; restyle = esattamente `style/voice → continuity → grammar → spelling` (senza structure); complete (stabilizzazione in fase 1) = solo `structure` e `continuity` su 1..M. Registri in `pass_scope`/`pass_progress` (Task 4).
- `## How each pass runs`: structure e continuity: per capitolo IN SEQUENZA (contro il ledger: facts-index compresso, mai il libro intero), un capitolo per subagent (`one chapter per dispatch`); ALL'INIZIO di ogni sweep sequenziale la `continuity/window/` viene RICOSTRUITA come sliding window della passata in corso (per il capitolo i: handoff dei capitoli (i−K)…(i−1)) — la window della fase 2 è congelata, ogni passata genera la propria; style/voice, grammar, spelling: per-file con subagenti PARALLELIZZABILI (un capitolo per subagent, contesto fresco) — i subagenti paralleli NON scrivono il registro della passata: ognuno scrive SOLO il proprio capitolo + il frammento per-capitolo `passes/registry-<pass>/ch-NN.md`, e il file `passes/registry-<pass>.md` è `aggregated by the orchestrator` a fine passata in ordine 01..NN (nessuna scrittura concorrente sul registro — è l'evidenza del Gate (b)); per restyle OGNI dispatch stile include `pilot.md` + style guide della bibbia come ancora few-shot (W4/matrix); ogni dispatch = role file del Task 12 + file input + canale di uscita prescritto.
- `## Contradiction protocol` (B2): il Continuity-checker confronta il capitolo con l'index: conflitto con provenienza ([ch.04] dice X, [ch.12] dice Y) → se la bibbia VALIDATA risolve univocamente: auto-fix `only the chapters in error` (contraddizione su un capitolo PRECEDENTE → dispatch mirato su quel capitolo, sempre one chapter per dispatch) + righe di index corrette + registro con entrambe le provenienze; se il canon è ambiguo: `stop and ask the user` — si scrive `passes/contradiction-NN.md` (entrambe le versioni + provenienza + schema di decisione), la passata su quel file si ferma, il ledger NON muta; la decisione dell'utente aggiorna bibbia/index e sblocca. Guardia B1: NESSUNA micro-passata (style/grammar/spelling) parte finché esiste un file STOP `passes/contradiction-*.md` APERTO.
- `## facts-index resync` (W5): DOPO la chiusura della passata structure E dopo ogni auto-fix di canon/contraddizione risolta: dispatch Continuity-checker per `resync facts-index` sui capitoli toccati (righe aggiornate con nuova provenienza) PRIMA che parta la passata successiva; a fine fase 3, resync finale mentre si prepara il gate.
- `## Diff registries`: un registro per passata: `passes/registry-structure.md` … `passes/registry-spelling.md`; la voce per capitolo (data, capitolo/file, problemi trovati (tipo e n.), changed yes/no, riepilogo per classe di intervento, UN campione before→after, contraddizioni eventuali con puntatore al file STOP) nasce come frammento `passes/registry-<pass>/ch-NN.md` e il registro della passata è l'aggregazione ordinata per capitolo dei frammenti (vedi How each pass runs); in work_mode complete il registro distingue la sezione `stabilization (phase 1)` da quella della fase 3. Registro = evidenza verificabile del diff (obiettivo 7).
- `## Gate — protocol (b)` (decisione utente 9): fine fase 3 → l'utente esamina i registri diff (ritionali per passata, con conteggi e campioni); l'orchestratore offre CAMPIONAMENTO (ri-lettura di capitoli scelti); la ri-lettura integrale è SEMPRE disponibile quando l'utente vuole rileggere tutto; il gate si chiude solo con l'approvazione esplicita → `gates.passes_approved: true` → `phase: "final_review"`.

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/passes.md tests/check.py
git commit -m "feat(skill): shared correction engine — macro→micro passes, contradiction protocol, resync (W4, W5, B1, B2)"
```

### Task 12: roles/structure-editor.md + roles/continuity-checker.md + roles/copy-editor.md

**Files:**
- Create: `skills/book-forge/references/roles/structure-editor.md`, `skills/book-forge/references/roles/continuity-checker.md`, `skills/book-forge/references/roles/copy-editor.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: strutture dei Task 4/8/11 (registri, index, invariants; canon = bibbia approvata).
- Produces: i tre prompt di specialisti per il motore fase 3: routine per passata (cosa cerca/tocca/non tocca/come registra). Il final-reviewer è del Task 13.

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `["skills/book-forge/references/roles/structure-editor.md", "skills/book-forge/references/roles/continuity-checker.md", "skills/book-forge/references/roles/copy-editor.md"]`;

`REQUIRED_HEADERS` (per OGNIUNO dei tre) =
```python
[
    "## Identity",
    "## Inputs",
    "## Pass routine",
    "## Output contract",
    "## Never",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/roles/structure-editor.md"]` =
```python
[
    "chapter cohesion",
    "the book flow",
    "do not write meta.json",
    "passes/registry-structure.md",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/roles/continuity-checker.md"]` =
```python
[
    "facts-index.md",
    "contradiction",
    "do not write meta.json",
    "passes/registry-continuity.md",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/roles/copy-editor.md"]` =
```python
[
    "style/voice",
    "grammar",
    "spelling",
    "do not write meta.json",
    "respect the voice: do not flatten intentional diction",
    "passes/registry-<pass>/ch-NN.md",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancanti ×3)**

- [ ] **Step 3: Scrivere i tre role file** (spec: manifesto passate, builder backlog):

- `structure-editor.md`: Identity: "You are the Structure Editor. You fix chapter cohesion and book flow — one chapter per dispatch, in reading order." Inputs: capitolo + outline contract + window; Routine: `chapter cohesion` (apertura/chiusura, ordine dei beat, promesse del capitolo mantenute) e contributo al `the book flow` (transizioni col capitolo precedente/successivo); spostamenti di paragrafi SENZA riscritture estese; Output: capitolo corretto + voce di registro (`passes/registry-structure.md`); Never: non toccare la bibbia/canon, non riscrivere la voce, `do not write meta.json`, non risolvere contraddizioni di canon (si passano al protocollo).
- `continuity-checker.md`: Identity: "You check the chapter against the continuity ledger and fix only what univocal canon fixes." Inputs: capitolo + `facts-index.md` + window + bibbia; Routine: confronto entità/fatti/promesse/thread; risolve SOLO a canon univoco; conflitto ambiguo → `contradiction` file STOP e fermo; tiene l'index aggiornato (duty anche per ledger update post-approvazione e resync W5 — Task 8/11); Output: capitolo (solo capitoli in errore) + righe index + registro `passes/registry-continuity.md`; Never: `do not write meta.json`, mai mutare l'index prima della decisione umana (canon ambiguo).
- `copy-editor.md`: Identity: "You are the Copy Editor. You run ONE micro pass at a time on one file: style/voice, grammar, or spelling — the dispatch names the pass." Routine delle tre: style/voice = contro la style guide (+ `pilot.md` come ancora few-shot quando mode restyle): allinea alla voce senza appiattirla — stringa esatta `respect the voice: do not flatten intentional diction` (dittongo, dialetto, ripetizioni volute restano); grammar = morfo-sintassi, accordi, tempi verbali; spelling = ortografia + nomi propri (cross-check con glossario e index) — mai normalizzare verso una varietà linguistica non voluta del libro; Output: file corretto + frammento per-capitolo `passes/registry-<pass>/ch-NN.md` (MAI il registro della passata: `passes/registry-style.md` e compagni sono `aggregated by the orchestrator` a fine passata — Task 11); Never: `do not write meta.json`, non toccare contenuti/struttura/canon, non fare interventi macro (fuori contratto), non cambiare lingua.

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/roles/structure-editor.md skills/book-forge/references/roles/continuity-checker.md skills/book-forge/references/roles/copy-editor.md tests/check.py
git commit -m "feat(skill): pass specialist roles — structure editor, continuity checker, copy editor"
```

### Task 13: references/final-review.md + roles/final-reviewer.md + check_role_paths

**Files:**
- Create: `skills/book-forge/references/final-review.md`, `skills/book-forge/references/roles/final-reviewer.md`
- Modify: `tests/check.py` (registri + `check_role_paths` + chiamata in `main`)

**Interfaces:**
- Consumes: Task 4 (`awaiting_fresh_session`, `degraded_non_independent`, invariante C3), Task 8 (index), Task 11 (registri), Task 3 (paths ruoli in SKILL.md).
- Produces: gate finale per-file con subagent FRESCHI per capitolo + aggregazione dei soli report (W5); check finale dell'integrità dei role path (SIGLA `ROLE_FILES`).

- [ ] **Step 1: Estendere `tests/check.py` — check_role_paths (contenuto esatto)**

Dopo `check_links`:

```python
ROLE_FILES = [  # every role path mentioned in SKILL.md must be exactly these
    "skills/book-forge/references/roles/researcher.md",
    "skills/book-forge/references/roles/drafter.md",
    "skills/book-forge/references/roles/structure-editor.md",
    "skills/book-forge/references/roles/continuity-checker.md",
    "skills/book-forge/references/roles/copy-editor.md",
    "skills/book-forge/references/roles/final-reviewer.md",
]
ROLE_PATH_RE = re.compile(r"references/roles/[a-z-]+\.md")


def check_role_paths(errors: list[str]) -> None:
    skill_rel = "skills/book-forge/SKILL.md"
    if not (ROOT / skill_rel).is_file():
        return
    mentioned = set(ROLE_PATH_RE.findall(read(skill_rel)))
    expected = {rel.split("skills/book-forge/")[-1] for rel in ROLE_FILES}
    for rel in ROLE_FILES:
        if not (ROOT / rel).is_file() and rel not in REQUIRED_FILES:
            errors.append(f"missing file: {rel}")
    if mentioned != expected:
        if expected - mentioned:
            errors.append(f"{skill_rel}: dispatch missing role paths {sorted(expected - mentioned)}")
        if mentioned - expected:
            errors.append(f"{skill_rel}: unknown role paths {sorted(mentioned - expected)}")
```

E dentro `main`, dopo `check_links(errors)`: `check_role_paths(errors)`.

- [ ] **Step 2: Registri (esatti)**

`REQUIRED_FILES` += `["skills/book-forge/references/final-review.md", "skills/book-forge/references/roles/final-reviewer.md"]`;

`REQUIRED_HEADERS["skills/book-forge/references/final-review.md"]` =
```python
[
    "## Fresh-session rule",
    "## Per-chapter dispatches",
    "## Aggregate the reports",
    "## User approval",
]
```
`REQUIRED_HEADERS["skills/book-forge/references/roles/final-reviewer.md"]` =
```python
[
    "## Identity",
    "## Inputs",
    "## Checks",
    "## Report contract",
    "## Never",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/final-review.md"]` =
```python
[
    "one fresh subagent per chapter",
    "never the chapter's own drafter",
    "nor its Phase 3 editor",
    "gates.passes_approved: false",
    "reports/final-review/ch-",
    "reports/final-review.md",
    "degraded_non_independent",
    "awaiting_fresh_session",
    "aggregates the per-chapter reports only",
]
```
`REQUIRED_SUBSTRINGS["skills/book-forge/references/roles/final-reviewer.md"]` =
```python
[
    "write only the report file",
    "do not write meta.json",
    "never rewrite",
    "fresh context",
]
```

- [ ] **Step 3: Run per verificare i fallimenti attesi**

Run: `uv run tests/check.py`
Expected: `FAIL — 2 problem(s)` — `missing file: skills/book-forge/references/final-review.md` + `missing file: skills/book-forge/references/roles/final-reviewer.md` (una volta ciascuno: il ramo missing di `check_role_paths` NON duplica — i role file sono già coperti da `REQUIRED_FILES`; quel ramo scatta solo per drift posteriore).

- [ ] **Step 4: Scrivere `final-review.md`** (spec: obiettivo 9; B4; W5):

- `## Fresh-session rule`: fine fase 3 → `phase: "final_review"`; in modalità inline senza sessione nuova: setta `awaiting_fresh_session: true` e STOP HARD (annuncio all'utente: riprendere in una sessione nuova); la sessione NUOVA si riconosce fresca (nessun turno di stesura/editing di questo libro nel proprio contesto), esegue `awaiting_fresh_session: false` e avvia il gate leggendo SOLO meta.json + questo file; con libri lunghi inline, i dispatch di review si frazionano in più sessioni fresche consecutive (mai accumulare N capitoli in un unico contesto inline); override self-review solo su richiesta ESPLICITA dell'utente → `degraded_non_independent: true` (mai entrambi i flag, C3) e la marcatura finisce nel rapporto finale.
- `## Per-chapter dispatches`: `one fresh subagent per chapter` (W5): dispatch del Final-reviewer (role path) per OGNI capitolo con input: capitolo + bibbia + righe facts-index del capitolo + registri rilevanti; `never the chapter's own drafter` — mai lo stesso agente che ha scritto/riscritto quel capitolo in fase 2 — `nor its Phase 3 editor` (nemmeno l'editor specialista che l'ha toccato in fase 3); UN subagent NON accumula mai più capitoli in contesto; ogni subagent scrive `reports/final-review/ch-NN.md`.
- `## Aggregate the reports`: l'orchestratore `aggregates the per-chapter reports only` — non ri-legge i capitoli: assembla `reports/final-review.md` (heading pinnato: Verdict per chapter; Unresolved markers; Style violations; Continuity breaks; Risk areas) + verdetto complessivo; se un capitolo NON supera: con conferma utente esplicita → retrocessione controllata `phase: "passes"` + `gates.passes_approved: false` → passata mirata sul capitolo + resync facts-index → nuovo Gate (b) → nuovo ingresso in `final_review` (in inline `awaiting_fresh_session` torna `true`: la sessione ha appena editato prosa).
- `## User approval`: rapporto aggregato all'utente → approvazione finale → `gates.final_approved: true`, `phase: "export"`; se override degraded: rapportare `degraded_non_independent` come prima riga del rapporto finale.

- [ ] **Step 5: Scrivere `roles/final-reviewer.md`**:

- `## Identity`: "You are the Final Reviewer. You are a fresh pair of eyes on ONE chapter — you never wrote or edited this book."
- `## Inputs`: capitolo, bibbia, righe facts-index pertinenti, registri passate; nient'altro — `fresh context`.
- `## Checks` (spec: gate finale): bibbia rispettata (canon/facts/voci); marker irrisolti (TODO/PLACEHOLDER/[...]); violazioni di stile contro la style guide; rotture di continuità (fatti/entità/promesse/thread in conflitto o mancanti); rispetto dei registri (le passate dichiarano fatto ciò che è fatto?).
- `## Report contract`: `write only the report file` `reports/final-review/ch-NN.md` — formato pinnato: Verdict (pass|fail) + Finding list (una per riga, con provenienza [ch.NN]/bible §… + gravità) + suggested action per finding.
- `## Never`: `never rewrite`/correggere la prosa; non toccare bibbia/index/registri; `do not write meta.json`; non guardare più capitoli (one chapter per dispatch).

- [ ] **Step 6: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/final-review.md skills/book-forge/references/roles/final-reviewer.md tests/check.py
git commit -m "feat(skill): fresh-session final gate — per-chapter reviewers, aggregated report (B4, W5)"
```

### Task 14: references/export.md — fase 5

**Files:**
- Create: `skills/book-forge/references/export.md`
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: Task 4 (`project.title/slug/language`, `phase: done`), comandi pandoc verificati in pre-piano.
- Produces: reference export. Ultima fase: nessun file di runtime viene modificato oltre exports/ e book.yaml.

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `skills/book-forge/references/export.md`; `REQUIRED_HEADERS` =
```python
[
    "## Check pandoc first",
    "## book.yaml",
    "## EPUB 3 export",
    "## DOCX export (optional)",
    "## Finish",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "--to epub3",
    "--split-level 1",
    "--toc",
    "Kindle Create",
    "the skill stops after export",
    "optional",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancante)**

- [ ] **Step 3: Scrivere `export.md`** (spec: obiettivo 10; decisione utente 7; Vincoli):

- `## Check pandoc first`: `pandoc --version`; se assente → messaggio chiaro: il manoscritto markdown è completo e valido anche senza; fornire le istruzioni (install link pandoc.org); NON tentare alternative di rendering.
- `## book.yaml`: creato dall'orchestratore da meta.json: `title`, `author` (chiesto all'utente qui se assente), `lang` (= `project.language`), data, `rights` opzionale. Anteprima per conferma prima dell'export (nessuna delle sezioni è un gate bloccante: è l'ultima azione dell'utente prima dell'export).
- `## EPUB 3 export` — comando esatto (glob dei capitoli in ordine NN):

```bash
pandoc --from markdown --to epub3 --split-level 1 --toc \
  --metadata-file book.yaml \
  --output exports/<slug>.epub \
  manuscript/*.md
```

  Note: `--split-level 1` = un file epub per capitolo (sostituisce il deprecato `--epub-chapter-level`); zero-padding dei nomi cap. garantisce l'ordine del glob; EPUB 3 così prodotto è importabile in `Kindle Create` (nota: cover design è un non-goal della skill, Kindle Create la accetta anche senza cover).
- `## DOCX export (optional)` — comando esatto:

```bash
pandoc --from markdown --to docx --toc \
  --metadata-file book.yaml \
  --output exports/<slug>.docx \
  manuscript/*.md
```

- `## Finish`: `phase: "done"`; `the skill stops after export` — nessun upload KDP nessuna pubblicazione (non-goal assoluti); l'utente riceve l'elenco file di exports/ e le istruzioni stesse per importare in Kindle Create (`"Import"` → epub).

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add skills/book-forge/references/export.md tests/check.py
git commit -m "feat(skill): pandoc export reference — EPUB 3 (Kindle Create) + optional DOCX"
```

### Task 15: README.md — installazione e sviluppo

**Files:**
- Create: `README.md` (root repo)
- Modify: `tests/check.py` (registri)

**Interfaces:**
- Consumes: albero del Task 1; comandi verificati solo runnable su push (setup-uv, uv sync, check).
- Produces: frontespizio pubblico della repo con instructions per skills.sh, pi e Claude Code + requirements + nota sviluppo.

- [ ] **Step 1: Registri (esatti)**

`REQUIRED_FILES` += `README.md`; `REQUIRED_HEADERS` =
```python
[
    "## What it does",
    "## The four jobs",
    "## How it works",
    "## Install — skills.sh",
    "## Install — pi",
    "## Install — Claude Code",
    "## Requirements",
    "## Development",
    "## Publishing checklist",
]
```
`REQUIRED_SUBSTRINGS` =
```python
[
    "npx skills add",
    "~/.agents/skills/",
    "~/.claude/skills/",
    "pandoc is optional",
    "uv run tests/check.py",
    "MIT",
]
```

- [ ] **Step 2: Run → Expected: FAIL (file mancante)**

- [ ] **Step 3: Scrivere `README.md`**:

- `## What it does`: 3 righe di cosa è (skill harness-agnostic per scrivere o correggere un libro intero: colloquio → bibbia → capitoli a gate umano → passate professionali → EPUB/DOCX; si ferma all'export).
- `## The four jobs`: create / complete / revise / restyle — una riga ciascuna (spec obiettivo 1).
- `## How it works`: pipeline 0–5 in 6 righe + albero del progetto libro + menzione che lo stato vive in meta.json e si può riprendere dopo mesi.
- `## Install — skills.sh`: comando della spec (verbatim, segnaposto owner): `npx skills add <owner>/book-forge@book-forge` — sostituire `<owner>` con l'owner reale GitHub alla pubblicazione; la `## Publishing checklist` verifica la sintassi live e, se il ref `@book-forge` non corrisponde al default del CLI, lo si allinea a publish-time.
- `## Install — pi`: `git clone https://github.com/<owner>/book-forge ~/.agents/skills/book-forge` — pi scopre ricorsivamente ogni directory con `SKILL.md` sotto `~/.agents/skills/` (location Agent Skills supportata nativamente da pi ≥1.6.0).
- `## Install — Claude Code`: `git clone https://github.com/<owner>/book-forge /tmp/book-forge && mkdir -p ~/.claude/skills && cp -r /tmp/book-forge/skills/book-forge ~/.claude/skills/` — oppure symlink.

N.d.B.: il nome del repo DEVE restare `book-forge` (skills.sh indicizza root/skills/<name>/SKILL.md).

- `## Requirements`: nessuna per il nucleo (fasi 0–4); `pandoc is optional` — servire solo per ingestire .docx e per l'export EPUB/DOCX; per .pdf in ingest serve un estrattore di testo (la skill lo dichiara se manca). Node/Python NON servono all'utente: `tests/` e `pyproject.toml` sono tooling di sviluppo del repo.
- `## Development`: clone → comando esatto `uv run tests/check.py` (uv ≥0.13, Python gestito da uv); indicare che i check congelano contratti (schema meta.json, header delle reference, warning W1–W5 come substrings) e che CI gira gli stessi.
- `## Publishing checklist`: (1) sostituire `<owner>` nel README; (2) verificare live `npx skills add <owner>/book-forge@book-forge` da macchina pulita (e allineare il ref `@book-forge` se il CLI usa un default diverso); (3) tag release; (4) dogfood dry-run della skill (progetto toy) prima della pubblicazione — consigliato ma fuori dal piano.
- Footer: licenza MIT con link a LICENSE.

- [ ] **Step 4: Run → Expected: OK. Commit:**

```bash
git add README.md tests/check.py
git commit -m "docs: README — jobs, pipeline, install (skills.sh / pi / Claude Code), requirements"
```

---

## Note di esecuzione

- **Lingua dei file creati**: ENGLISH per skill e repo (Global Constraint 1). I .md della skill parlano all'agente ("you are…"), non all'utente finale.
- **`uv run` sempre**: ogni invocazione di Python passa da `uv run` (es. Task 1 Step 5: `uv run python -c …`). MAI usare `python` da solo — sulla macchina di build è lo stub dello Store (`Python was not found`) — e MAI separare `python` dal prefisso `uv run` quando si copia un comando.
- **Path inline-code ovunque + esecuzione strettamente sequenziale**: in TUTTI i `.md` della skill, ogni path `references/…` (inclusi i role file) si scrive come inline code tra backtick, MAI come hyperlink markdown `[…](…)`: le forward-reference (Task 5→6, 6→9, 8→9, 9→11) romperebbero `check_links`, e dentro `references/*.md` un hyperlink relativo si risolverebbe in `references/references/…`; i Task 1–15 si eseguono STRICTLY SEQUENTIAL — tutti modificano `tests/check.py` (registro condiviso), nessun dispatch in parallelo.
- **Espansione contenutistica**: ogni sezione pinnata con 4–10 righe: il worker Espande in prosa inglese rispettando gli header esatti e le substring ancorate; la spec (collegata nel header del piano) è l'autorità semantica; i valori pinnati in tabella qui sono stringhe vincolanti.
- **Autocontrollo del worker**: dopo ogni task, il grep delle substring PInnate deve funzionare; contestualmente rileggere il report contro il diff (regola AGENTS.md: claim con file:linea).
- **Il committ finale del piano**: `git commit -m "docs: implementation plan…" NON serve` — il piano è già committato dall'orchestratore; i task sopra partono dal commit con la spec congelata.

## Changelog / Emendamenti

- **2026-11-25 · Amendamento 1** (da plan-validator round 1 — verdetto BLOCKED, 1 blocker + 5 warning; report: `docs/superpowers/plans/2026-11-25-plan-validator-report.md`):
  - **Task 4 Step 2 (blocker)** — C6 riscritto: check d'ordine (`idx != sorted`) applicato SOLO ai subset del mode revise; create/complete pinnati per uguaglianza esatta con l'ordine completo macro→micro; restyle pinnato per uguaglianza esatta con `[style, continuity, grammar, spelling]` (voce prima per design — spec matrice (iv) + W4). Rimuove il contratto insoddisfacibile: prima, l'ordine restyle `[style, continuity, …]` violava PASS_ORDER e la fixture valida `meta-restyle-final-review.json` non poteva passare.
  - **Task 4 Step 6** — regola 7 di `state.md` espansa con i contratti per modalità (mirror del C6 emendato).
  - **Task 2 (W4)** — `check_links` salta anche `graphify-out/` (output locale del tool, con link relativi non verificabili dal piano).
  - **Task 13 Step 1 (W5)** — `check_role_paths` non duplica i missing già coperti da `REQUIRED_FILES` (`rel not in REQUIRED_FILES`); **Step 3** expected aggiornato a `FAIL — 2 problem(s)`.
  - **Task 3 Step 3 (W3)** — disciplina esplicita: path `references/roles/*.md` in SKILL.md sempre inline code, mai hyperlink (link-check del Task 2).
  - **Note di esecuzione (W2)** — aggiunta regola «`uv run` sempre, mai separare `python` dal prefisso» (Task 1 Step 5 resta `uv run python -c …`, unico uso inline documentato).
- **2026-11-25 · Amendamento 2** (da plan-validator round 2 — PASS con warning; R2-1 + note N1/N2):
  - **Task 4 Step 4 (R2-1)** — `meta-invalid-bad-enum.json`: `"web_available": false` (era `null`): con l'enum invalido di `phase` scatta SOLO l'errore di enum dello schema; prima la notazione violava anche C4 e il motivo di rifiuto non era esclusivo. Aggiunta nota a piè della notazione.
  - **N1** — chiarimento: le etichette W2…W5 usate nel Changelog dell'Amendamento 1 si riferiscono ai finding f2…f5 del round 1 di plan-validator, NON ai warning oracle W1–W5 (che restano gli ID della tabella «Warning oracle → task» in testa al piano).
  - **N2** — refuso corretto nel Changelog dell'Amendamento 1 («voi link relativi» → «con link relativi»).
- **2026-11-25 · Amendamento 3** (da oracle freeze piano round 1 — verdetto FREEZE BLOCCATO: 3 blocker + 4 warning; verdetto integrale: `docs/superpowers/plans/2026-11-25-oracle-plan-freeze-verdict.md`):
  - **Blocker O1 — C8/routing ingestione** — Task 4 Step 2: C8 scatta SOLO da Gate 1 in poi (`phase not in ("intake","bible") or bible_approved`), così lo stato legittimo `phase: "bible"` con capitoli non ancora importati non è più bocciato; Task 3: routing `phase × work_mode` esplicito per la fase `bible` (create→bible.md; esistenti senza capitoli→ingest.md; con capitoli importati→reconstruction.md) + substring `references/ingest.md` in SKILL.md; Task 4 Step 6 state.md: regola 9 (risoluzione `<phase>` via tabella, mai nome letterale); Task 7 bible.md: riga di redirect per work_mode ≠ create; Task 5: `chapters: []` chiarito per OGNI work_mode.
  - **Blocker O2 — contratto mode complete** — Task 9: lo sweep estrae anche sintesi purpose/beat → `outline.md` assemblato sui capitoli importati + handoff window degli ultimi K capitoli importati; Gate 1 (complete/revise): la style guide descrittiva diventa NORMATIVA con la validazione utente; in complete il Gate 1 approva anche i contratti M+1..N (integrati col colloquio) e, conclusa la stabilizzazione, l'orchestratore registra M+1..N (`planned`, `written`) PRIMA di `phase: "chapters"`; Task 7 Gate 1: init `chapters` 1..N da outline (create); Task 10 Closing: all'ultimo `approved` → `phase: "passes"` + init `pass_scope`/`pass_progress` per C6.
  - **Blocker O3 — race sui registri paralleli** — Task 11 + Task 12: i subagenti paralleli scrivono SOLO il frammento `passes/registry-<pass>/ch-NN.md`; il registro della passata è `aggregated by the orchestrator` a fine passata (ordine 01..NN); output contract del copy-editor aggiornato.
  - **Warning O4 — window e sweep** — Task 8/11: ogni passata sequenziale RICOSTRUISCE la window come sliding window della passata in corso; registri con sezione `stabilization (phase 1)` distinta dalla fase 3; Task 8/9: ammessa popolazione PROVISIONAL pre-Gate-1 di facts-index (Status `provisional`) + `research/reconstruction-notes.md` passate in input a ogni dispatch Duty B (il capitolo 12 vede i fatti del 04 senza caricare i capitoli precedenti).
  - **Warning O5 — economia di contesto in ingest + esecutore pilota** — Task 6: split basato su heading search/line ranges, MAI lettura integrale di `research/manuscript-raw.md` in contesto LLM; Task 9 restyle: pilota prodotto da dispatch di copy-editor (inline code) con round-trip fino a approvazione Gate 1.
  - **Warning O6 — transizioni fase 4 e invarianti** — state.md regole 3 e 8 estese (riconoscimento sessione fresca + retrocessione controllata final_review→passes + batching inline su più sessioni fresche); final-review: esclude anche `nor its Phase 3 editor` dello stesso capitolo; C5 esteso a tutte le fasi post-stabilizzazione (vieta di retrocedere da `done`); C7 vieta `planned` da `passes` in poi; passes.md: guardia STOP-file aperti (B1) + dispatch mirato sul capitolo precedente.
  - **Warning O7 — igiene di esecuzione e portabilità** — Note di esecuzione: path inline-code GLOBALI (forward-reference Task 5→6/6→9/8→9/9→11) e Task 1–15 STRICTLY SEQUENTIAL; drafting.md fallback one-shot stateless di `the same drafter` (la continuità vive nei file, non nell'istanza); slug ASCII con translitterazione (fallback `chapter-NN`); regex `project.language` allargata a `^[a-z]{2,3}(-[A-Za-z0-9]{2,8})*$` (accetta BCP-47 tipo `zh-Hans`, `es-419`); README allineato al comando spec `npx skills add <owner>/book-forge@book-forge` con verifica ref a publish-time; refusi residui puliti (Task 6 «Aggiornare… NO:», Task 13 «kk:").
  - **Impatto fixture: zero** — nessuna delle 12 fixture cambia esito o motivo esclusivo di rifiuto (desk-check: complete è `phase: bible`; nessuna valida ha `planned` in fasi post-capitoli; le C5/C7 estese aggiungono solo vincoli a stati finora non campionati).
- **2026-11-25 · Amendamento 4** (escalation worker Task 2, confermata dall'autore):
  - **Task 2 — `check_links` ignora il codice quotato** — aggiunti `FENCE_RE` (`` r"`{3}.*?`{3}`, re.DOTALL ``) e `CODE_SPAN_RE` (` `` r"`[^`\n]*`" ``) + funzione `strip_code(text)` applicata al testo PRIMA di estrarre i link: fenced block e inline code span non sono prosa markdown e i loro esempi `[x](path)` non vanno validati. Motivo: il piano stesso (Amendamento 3, regola inline-code) e il verbale oracle contengono esempi inline-code legittimi che il LINK_RE naive segnava come link rotti (`docs/superpowers/plans/2026-11-25-book-forge-skill.md:1678`, `…oracle-plan-freeze-verdict.md:92`) — l'assunzione "docs senza link relativi" del pre-piano era stata invalidata dagli artefatti post-freeze. Expected dello Step 2 invariato (`OK — all checks passed`). — Se l'emendamento fosse sbagliato: costo = un link rotto reale dentro un code span non verrebbe rilevato; caso mai verificato negli artefatti di questo repo.
- **2026-11-25 · Amendamento 5** (escalazione worker Task 2, round 2, confermata dall'autore):
  - **Task 2 — span a backtick VARIABILE in `strip_code`** — `FENCE_RE` diventa `r"`{3,}.*?`{3,}"` e `CODE_SPAN_RE` (monobacktick/monoriga: si sfasava sugli span DOPPIO-backtick — es. la prosa stessa del changelog di Amendamento 4) è sostituito da `SPAN_RE = r"(?<!`)(`+)(?!`)(.*?)(?<!`)\\1(?!`)"` con re.DOTALL: pairing a lunghezza variabile con lookaround — semantica markdown corretta anche per span che citano codice contenente backtick. Opzione B ( riscrivere la prosa del changelog per evitare i doppi backtick ) rifiutata: il doppio backtick è markdown legittimo e l'harness deve reggerlo; opzione C ( rosso accettato ) rifiutata. Verifica del worker su tutto il repo (scratch non committato): zero link segnalati. Expected Step 2/Step 3 invariati. — Se sbagliata: costo = potenziale mispairing in combinazioni esotiche di backtick ( non presenti in questo repo ).
