# Report plan-validator — piano di implementazione book-forge

Piano: `docs/superpowers/plans/2026-11-25-book-forge-skill.md` · Dossier: `docs/superpowers/plans/2026-11-25-plan-validator-dossier.md`
Nota: il validatore gira senza tool di scrittura — il report torna nel canale e l'orchestratore lo deposita qui. Ogni round è una sezione.

## Round 1 — repo @ `eaefc58` — verdetto: **BLOCKED** (blocker = 1 · warning = 5)

Data: 2026-11-25 · Single-shot sul corpus del dossier · Desk-check: snippet verbatim, expected dei run, perimetri, ordine, simulazione delle 12 fixture attraverso `check_schema` + `check_meta_invariants`.

### Finding

#### 1 — BLOCKER — Task 4 Step 2 (`check_meta_invariants`, C6) + Step 4/5 (fixture restyle) + Task 9 Step 3

**Mismatch:** l'invariante C6 impone l'ordine canonico `PASS_ORDER = ["structure", "continuity", "style", "grammar", "spelling"]` a TUTTE le modalità:

```python
idx = [PASS_ORDER.index(p) for p in scope]
if idx != sorted(idx):
    errs.append("pass_scope violates macro->micro order: " + " -> ".join(PASS_ORDER))
```

ma lo scope restyle pinnato dal piano stesso (Task 4 Step 2: uguaglianza esatta `["style", "continuity", "grammar", "spelling"]`; Task 9: "`pass_scope` = [style, continuity, grammar, spelling] (C6)") e dalla spec congelata (matrice: "stile (pilota come ancora) → continuità → grammatica → ortografia"; W4) ha `style` PRIMA di `continuity`. Desk-check: `idx = [2, 1, 3, 4]`, `sorted(idx) = [1, 2, 3, 4]` → C6 spara `"pass_scope violates macro->micro order"` su:
- `tests/fixtures/meta-restyle-final-review.json` (VALIDA dichiarata) → Task 4 Step 5 `Expected: OK — all checks passed` **impossibile**;
- derivate `meta-invalid-flags.json` e `meta-invalid-scope.json`: rifiutate anche per un motivo NON dichiarato (violano "rifiutata per il motivo dichiarato", dossier Regole §5).

Nessun `pass_scope` può soddisfare contemporaneamente l'ordine C6 e l'uguaglianza restyle: contratto insoddisfacibile per il mode restyle; a runtime ogni progetto restyle conforme alla spec verrebbe bocciato dall'harness.

**Fix suggerita:** in C6 applicare il check d'ordine solo al mode revise (per restyle l'uguaglianza esatta pinnata garantisce già l'ordine); aggiornare il contratto C6 in `state.md`. Nessuna modifica alla spec (frozen) né alle fixture.

#### 2 — WARNING — Task 1 Step 5 (perimetro comando)

`uv lock && uv run python -c "import jsonschema, …"`: unico punto con `python` inline; il dossier vieta `python`/`pytest` nudi. Qui è `uv run python` (CPython gestito, non lo stub Store — pattern provato §1), quindi attuabile, ma il worker potrebbe estrarre il comando senza prefisso. **Fix:** nota di esecuzione «mai separare `python` da `uv run`».

#### 3 — WARNING — Task 3 Step 3/4 vs `check_links` (Task 2)

Task 3 prescrive in SKILL.md i path `references/state.md`, `references/intake.md`, `references/roles/*.md` come substring, ma NON prescrive (a differenza dei Task 7/8: "citare come inline code, no hyperlink") che siano inline code. Se il worker li rende hyperlink, `check_links` produce `broken link -> references/roles/researcher.md` ecc. allo Step 4, perché quei file esistono solo dai Task 4+ → expected `OK` non raggiunto. **Fix:** estendere a Task 3 la disciplina inline-code dei Task 7/8.

#### 4 — WARNING — Task 2 Step 2 (assunzione link-check fuori perimetro provato)

`check_links` usa `ROOT.rglob("*.md")`: copre anche `graphify-out/` ( GRAPH_REPORT.md verbatim nel corpus, zero link relativi ✓ — ed eventuale `wiki/`, NON incluso nel dossier). Se il wiki contiene link relativi a file non-.md, lo smoke fallisce per cause esterne al piano. **Fix:** estendere lo skip di `check_links` a `graphify-out` o verificare il wiki prima del dispatch.

#### 5 — WARNING — Task 13 Step 1 (`check_role_paths`, doppio conteggio)

Il role file mancante `roles/final-reviewer.md` è segnalato sia da `check_required_files` sia da `check_role_paths` → due errori identici `missing file: …`. L'expected è solo `FAIL` (senza conteggio), non rompe nulla, ma è rumore diagnostico. **Fix:** in `check_role_paths` segnalare i mancanti solo se non già in `REQUIRED_FILES`, o accettare il duplicato come noto.

#### 6 — WARNING — Dossier §Corpus/§4 vs GRAPH_REPORT.md (claim commit incoerente)

Il dossier dichiara il grafo "fresco (built from commit `6cc7395`)" e il repo "@ `6cc7395`", ma `graphify-out/GRAPH_REPORT.md` riporta "Built from commit: `eaefc584`" (= HEAD del brief: l'hook post-commit l'aveva già aggiornato). Il grafo è PIÙ fresco del claim. Nessun impatto sul lint; **fix:** allineare il claim (nota: l'hook post-commit aggiorna a ogni commit).

### Verifiche passate (sintesi desk-check round 1)

- **Snippet verbatim:** core Task 2 (registri; `check_frontmatter` riga-per-riga vs frontmatter Task 3: `name: book-forge` ✓, description una riga ~350 ≤1024 ✓); API jsonschema Task 4 = pattern provato §1 ✓; `format: "date"` solo annotation ✓; pyproject Task 1 = §1 verbatim ✓; CI `uv sync --frozen` dopo commit di `uv.lock` nello stesso task ✓; `.gitignore` (Step 2) precede il primo `uv run` (Step 5) ✓; flag pandoc Task 6/14 = §2 ✓; nessun task esegue pandoc ✓; nessun `pytest`/CLI jsonschema nudi ✓.
- **Expected dei run:** Task 2 Step 2/3 ✓; Task 3 Step 2 ✓; Task 4 Step 3 `FAIL — 12 problem(s)` ✓; Task 13 Step 3 FAIL con doppio missing (vedi finding 5) ✓.
- **Fixture:** 6 valide → zero errori TRANNE `meta-restyle-final-review.json` (finding 1); 6 invalide → ciascuna rifiutata per il motivo dichiarato (bad-enum e block-size via schema — confermato dal log verbatim §1; gates→C2, file-number→C1, flags→C3, scope→C6) più l'errore C6 spurio sulle due derivate restyle (finding 1).
- **Copertura/ordine:** W1–W5, B1–B4 tracciati; interfacce consumate sempre prodotte da task precedenti o pinnate; forward-reference role file come inline code nei Task 7/8/11 ✓; `ROLE_FILES` (6) == substrings Task 3 == file creati Task 9/10/12/13 ✓; regex matcha tutti e 6 i nomi ✓; perimetri disgiunti eccetto `tests/check.py`, sempre modificato in-step con ordine fail→implement→pass→commit ✓.
- **Rischio residuo:** wiki `graphify-out/` non nel corpus (finding 4); `npx skills add` e CI GitHub dichiarati publish-time-only ✓; substring da copiare ESATTE (accenti/frecce `→`, em-dash `—`) grep-verificabili a ogni step.

### Esito round 1

**Verdetto: BLOCKED — blocker: 1, warning: 5.** Blocker: find 1 — Task 4, C6: l'ordine macro→micro imposto a `pass_scope` contraddice lo scope restyle `style→continuity→grammar→spelling` pinnato da spec e piano; la fixture valida `meta-restyle-final-review.json` non può passare e l'expected `OK` dello Step 5 è impossibile. Fix dell'autore: **Amendamento 1** (Changelog in coda al piano). Round 2: rilancio del gate sui delta.
