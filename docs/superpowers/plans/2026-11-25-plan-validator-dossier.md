# Dossier plan-validator — piano di implementazione book-forge

Data: 2026-11-25 · Piano sotto esame: `docs/superpowers/plans/2026-11-25-book-forge-skill.md` · Modalità: **lint meccanico del piano (gate pre-dispatch)**

## Regole del verdetto

- Sei **single-shot**: il corpus sotto è l'input COMPLETO. Non esplorare il codebase, non aprire file non elencati. Il repo non contiene codice: tutto ciò che esiste è elencato qui.
- Verifica in ordine di priorità:
  1. **Snippet prescritti verbatim vs realtà**: firme, shape di ritorno, valori ai casi limite/assenti, default — contro le evidenze verbatim di questo dossier (unica "realtà" disponibile: provate dall'orchestratore sulla macchina di build il 2026-11-25).
  2. **Output attesi dei run** (i passi "Run → Expected") vs la logica del codice pinnato: il piano fissa le stringhe di errore/esito — verifica che il codice prescritto le produca davvero in quello step (file già creati in step precedenti inclusi).
  3. **Perimetri**: snippet/API esterne che il task assume senza prescriverle; snippet che toccano file fuori dal task; task che consuma un'interfaccia che nessun task precedente produce.
  4. **Ordine**: step interni ai task (fail→implement→pass→commit) e ordine tra task (dipendenze dichiarate negli Interfaces).
  5. **Fixture vs invarianti**: ogni fixture dichiarata INVALIDA deve essere rifiutata per il motivo dichiarato; ogni VALIDA deve passare schema + tutte le invarianti senza errori residui.
- Severità: **blocker** = snippet non attuabile/contraddetto, expected impossibile, interfaccia mancante, ordine rotto. **warning** = attuabile ma fragile/implicito, da attuare senza fermare il dispatch.
- Ripporta ogni finding con: task/step del piano, severità, evidenza (riga citata), fix suggerita.
- Verdetto finale: `PASS` / `PASS con warning` / `BLOCKED`.
- Scrivi il report in `docs/superpowers/plans/2026-11-25-plan-validator-report.md` — è l'UNICO file che puoi scrivere.

## Corpus del dossier (leggi tutto, null'altro)

1. `docs/superpowers/plans/2026-11-25-book-forge-skill.md` — il piano (15 task; snippet di codice, 12 fixture, expected output, comandi) — con **Amendamento 1** applicato (sezione `## Changelog / Emendamenti` in coda).
2. `docs/superpowers/specs/2026-11-25-book-forge-design.md` — spec CONGELATA, FREEZE OK round 2 (autorità semantica; no Findings su di essa: è frozen).
3. `graphify-out/GRAPH_REPORT.md` — report del grafo. NB: mantenuto fresco dall'hook post-commit `graphify update` (auto-maintenance AGENTS.md): il file si aggiorna a OGNI commit del repo, quindi il suo `Built from commit` sarà sempre il commit corrente o più recente del corpus; per il gate vale il contenuto del file, non il confronto con un commit specifico citato altrove.
4. `docs/superpowers/plans/2026-11-25-plan-validator-report.md` — Round 1 (verdetto BLOCKED: 1 blocker + 5 warning) — i finding che l'Amendamento 1 risolve.
5. Questo dossier (evidenze ambiente verbatim + istruzioni round 2 sotto).

## ROUND 2 — istruzioni

- Il piano è cambiato SOLO dove dice l'`Amendamento 1` (Changelog in coda al piano). Nessun altro delta è ammesso: se trovi modifiche fuori dai punti elencati nel Changelog, è un finding (perimetro violato).
- Verifica per il round 2:
  1. **Nuovo C6** (Task 4 Step 2): desk-check TUTTE le 12 fixture (incluse le due derivate restyle di finding 1) — le 6 valide devono passare schema+C1–C8 senza alcun errore; le 6 invalide devono essere rifiutate ESATTAMENTE per i motivi dichiarati (2 via schema, 4 via invarianti: gates→C2, file-number→C1, flags→C3, scope→C6-restyle-equality).
  2. **Coerenza C6 ↔ resto del piano**: regola (7) di state.md (Task 4 Step 6), Task 9 Step 3 (`(C6)`), Task 11 ordine/ambiti — tutte allineate con il C6 emendato (restyle = [style, continuity, grammar, spelling] voce prima; create/complete = ordine completo; revise = subset in ordine macro→micro).
  3. **W4**: nuovo expected Task 13 Step 3 (`FAIL — 2 problem(s)`, no duplicati) e `check_role_paths` con guardia `rel not in REQUIRED_FILES`.
  4. **W3**: disciplina inline-code aggiunta a Task 3 Step 3 coerente con `check_links` (che ora salta anche `graphify-out`/ — W4|finding 4).
  5. **W2**: nota di esecuzione «`uv run` sempre / mai separare `python` dal prefisso» presente; Task 1 Step 5 resta `uv run python -c …` (utilizzabile per il dossier §1).
  6. **W6**: i claim di commit del dossier sono deprescati (vedi corpus punto 3) — le righe §«Verità d'ambiente» non citano più commit specifici come vincolo.
- Esci con verdetto round 2 (`PASS` / `PASS con warning` / `BLOCKED`) e conteggio finding. Se non hai tool di scrittura, restituisci il report nel canale: l'orchestratore lo appende al file del report come `## Round 2`.

## Verità d'ambiente — evidenze verbatim (orchestratore, 2026-11-25, macchina di build Windows 11)

### 1. Python e uv — PROVATO con scratch dentro il repo (poi rimosso)

- `python --version` → `Python was not found…Microsoft Store` (stub Store): **vietato** prescrivere `python`/`pytest` nudi; tutto il piano passa da `uv run` (il piano li usa ovunque — verifica che NESSUN task prescriva `python`/`pytest`/`jsonschema` CLI nudi).
- `uv --version` → `uv 0.13.5 (46776a95d 2026-10-21 x86_64-pc-windows-msvc)`.
- Pyproject provato (identico a quello pinnato nel Task 1):

```toml
[project]
name = "book-forge-dev"
version = "0.1.0"
description = "…"
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.23"]

[tool.uv]
package = false
```

- `uv run verify.py` → sceglie CPython gestito, crea `.venv`, risolve le dipendenze, esegue. Log verbatim:

```
Using CPython 3.13.17
Creating virtual environment at: .venv
Installed 5 packages in 36ms
good errors: 0
bad errors: 2
 - phase : 'drafting' is not one of ['intake', 'bible', 'chapters', 'passes', 'fi…
 - validation_mode/block_size : 1 is less than the minimum of 2
```

- Pattern API jsonschema provato (identico, salvo uno schema minimale, a quello pinnato nel Task 4 — `check_schema`):

```python
import json
from pathlib import Path
import jsonschema

schema = json.loads(Path("mini.schema.json").read_text(encoding="utf-8"))
cls = jsonschema.validators.validator_for(schema)
cls.check_schema(schema)
validator = cls(schema)
errs = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
```

Confermato su questa macchina: `validator_for` onora `$schema` draft 2020-12, `check_schema` solleva su schema malformato, `iter_errors` produce errori con `message` e `absolute_path`, enum/`if`+`then`/`minimum` funzionano. NOTA: `format: "date"` NON è validato di default da jsonschema senza format-assertion (il piano lo ha per `project.created`: è annotation, non vincolo — verifica che nessun expected finga il contrario).

### 2. Pandoc — NON installato sulla macchina (`which pandoc` → vuoto)

Nessun task del piano esegue pandoc. I flag prescritti (Task 6 ingest .docx; Task 14 export) verificati sui documenti ufficiali pandoc.org (via Context7, 2026-11-25):

- Output EPUB 3: `--to epub3` (formato writer `epub3`) ✓
- `--split-level` sostituisce `--epub-chapter-level` (quest'ultimo DEPRECATO ma funzionante; fonte: release notes pandoc 3.0) — il piano usa `--split-level 1` ✓
- `--toc` include la TOC nei formati docx/epub (stanno già in standalone; nessun `-s` richiesto) ✓
- `--metadata-file <yaml>` e campi `title`/`author`/`lang` standard ✓
- `--wrap=none` (usato da Task 6 per non refoldare la prosa) ✓
- `--epub-cover-image` esiste: il piano NON lo usa (cover = non-goal della spec) ✓
- pandoc NON legge `.pdf` COME INPUT (PDF è solo tra i formati di output): il piano prescrive estrattore dedicato (W2) ✓

### 3. pi 1.6.0 — estratto verbatim da docs/skills.md

> "Pi implements the Agent Skills specification […] a skill is a directory containing SKILL.md […] Most invalid fields produce warnings rather than stopping startup."
>
> "Directories containing SKILL.md are discovered recursively. […] Pi also supports the Agent Skills locations ~/.agents/skills/ and .agents/skills/."
>
> "Names use lowercase letters, numbers, and hyphens… They can contain at most 64 characters; descriptions can contain at most 1024."
>
> "Malformed SKILL.md files and declared skills without descriptions are not loaded. Name collisions keep the first discovered skill and produce a warning."

Il piano prevede: name `book-forge` (kebab, ≤64) ✓; description pinnata ~350 caratteri ≤1024 ✓; README pi via `~/.agents/skills/` ✓ — verifica coerenza Task 3 frontmatter vs Task 2 `check_frontmatter` (riga `name: book-forge`, description su UNA riga: il check legge la description riga-per-riga).

### 4. Repo, infrastruttura, e cose NON verificabili localmente

- Repo `main`: nessun codice → nessun conflitto possibile con file esistenti. Contenuto docs/: spec + dossier oracle + piano + dossier plan-validator + report plan-validator (round 1+). `graphify-out/` è output locale del tool (gitignored, non skill, non documentazione).
- `node v26.13.0` presente ma inutilizzato dal piano (harness uv).
- `.git/hooks/post-commit` attivo con `graphify update . >/dev/null 2>&1 || true` (auto-maintenance AGENTS.md).
- `.gitignore` attuale NON contiene `.venv/`: il piano (Task 1 Step 2) la aggiunge in tempo — verifica che lo step preceda il primo `uv run` che crea la venv (Step 5 genera `uv.lock`: la venv `.venv/` viene creata lì).
- CI (Task 1): GitHub-only, non eseguibile localmente. `astral-sh/setup-uv@v5` è la major documentata dell'azione ufficiale; `uv sync --frozen` richiede `uv.lock` committato (Task 1 Step 5 lo genera e lo committa nello stesso task ✓).
- `npx skills add <owner>/book-forge` (Task 15): sintassi NON verificabile prima della pubblicazione su GitHub — il piano la dichiara apertamente nella `## Publishing checklist` con la verifica live a publish-time. `<owner>` è un placeholder intenzionale.

## Mappa snippet → dove verificarli

| Snippet pinnato | Task | Contro-realtà |
|---|---|---|
| `tests/check.js`… `tests/check.py` core (re/sys/pathlib) | Task 2 | nuovo file, zero API esterne; è il produttore degli expected string di TUTTI i task successivi (`missing file:`, `missing fixture:`, `TODO`, `FAIL — N problem(s)`, `OK — all checks passed`) |
| `check_meta_invariants` C1–C8 + `check_schema` | Task 4 | API jsonschema provata (§1); traccia 6 fixture valide→zero errori e 6 invalide→esattamente i motivi dichiarati (2 via schema, 4 via invarianti) |
| `meta.schema.json` draft 2020-12 | Task 4 | self-contained: enum/required/if-then/pattern/additionalProperties; `validator_for` lo onora via `$schema` |
| 12 fixture `tests/fixtures/meta-*.json` | Task 4 | valori conformi a schema+invarianti come da dichiarazioni del piano |
| `ROLE_FILES` + `check_role_paths` | Task 13 | regex `references/roles/[a-z-]+\.md`; i 6 path coincidono con le substrings pinnate in SKILL.md (Task 3) e con i file creati nei Task 9/10/12/13 |
| `pyproject.toml` + `ci.yml` | Task 1 | pyproject provato (§1); CI solo coerenza sintattica/ordine step |
| comandi pandoc ingest (Task 6) / export (Task 14) | 6, 14 | flag verificati (§2); esecuzione rinviata a runtime utente |
| README + comandi install | Task 15 | pi (§3); skills.sh dichiarato publish-time-only |

## Escalation

- Blocker → l'autore corregge il piano e si rilancia il gate (max 2 giri), poi escalation utente.
- Warning → attuati come ammendamenti al piano prima del dispatch worker (o Note di esecuzione).
