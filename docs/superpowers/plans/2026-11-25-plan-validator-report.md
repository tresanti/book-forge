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


## Round 2 — repo @ `21344ad` + Amendamento 2 — verdetto: **PASS con warning** (blocker 0 · warning 1 + 2 note)

> Testo verbatim del validatore (run e077d912). Le sue conclusioni sono pre-Amendamento 2: R2-1, N1 e N2 sono attuati dall'Amendamento 2 (Changelog del piano).

Piano: `docs/superpowers/plans/2026-11-25-book-forge-skill.md` (con Amendamento 1) · Dossier: `docs/superpowers/plans/2026-11-25-plan-validator-dossier.md` · Repo @ `21344ad` · Grafo: `Built from commit: 21344ade` = HEAD del brief ✓ (hook post-commit, corpus punto 3).

## Verdetto Round 2: **PASS con warning** — blocker: 0 · warning: 1 (+ 2 note non-finding)

Nessun tool di scrittura disponibile: il report torna nel canale; l'orchestratore lo appende a `docs/superpowers/plans/2026-11-25-plan-validator-report.md` come `## Round 2`.

---

## 1. Delta Amendamento 1 — verifica puntuale

| Punto Changelog | Esito | Evidenza |
|---|---|---|
| Task 4 Step 2 — C6 riscritto (blocker R1) | ✅ ATTUATO | Check d'ordine `idx != sorted(idx)` ora nel solo ramo `elif mode == "revise"`; create/complete per uguaglianza `scope != PASS_ORDER`; restyle per uguaglianza `scope != ["style", "continuity", "grammar", "spelling"]`. Il contratto insoddisfacibile è rimosso: nessun ramo impone più PASS_ORDER al restyle. |
| Task 4 Step 6 — regola (7) state.md | ✅ ATTUATO | «create/complete = tutte e cinque in ordine macro→micro; revise = sottoinsieme non vuoto in ordine macro→micro…; restyle = esattamente [style, continuity, grammar, spelling] (voce prima per design, W4)» — mirror fedele del C6 emendato. |
| Task 2 — `check_links` salta `graphify-out/` (R1 f4) | ✅ ATTUATO | `if ".git" in path.parts or "node_modules" in path.parts or "graphify-out" in path.parts: continue` — presente nel core verbatim. Rischio wiki fuori corpus eliminato. |
| Task 13 Step 1 — guardia anti-duplicato (R1 f5) | ✅ ATTUATO | `if not (ROOT / rel).is_file() and rel not in REQUIRED_FILES:` — il ramo missing non duplica i file già in registro. |
| Task 13 Step 3 — expected `FAIL — 2 problem(s)` | ✅ ATTUATO + desk-check ✓ | Al Step 3: `check_required_files` → 2 missing (final-review.md, roles/final-reviewer.md); `check_role_paths` → ramo missing skippato (entrambi in REQUIRED_FILES), `mentioned == expected` (SKILL.md del Task 3 cita tutti e 6 i path, regex li matcha anche dentro backtick) → 0 errori; headers/substrings dei file mancanti skippati; link-check ok (inline code). Totale esatto: **2**. |
| Task 3 Step 3 — disciplina inline-code (R1 f3) | ✅ ATTUATO | Paragrafo «Disciplina link-check (vincolante)»: path `references/…` e `references/roles/*.md` sempre inline code, mai hyperlink; coerente con `check_links` (che ora salta anche graphify-out). |
| Note di esecuzione — «`uv run` sempre» (R1 f2) | ✅ ATTUATO | Nota presente: «MAI usare `python` da solo… MAI separare `python` dal prefisso `uv run`». Task 1 Step 5 resta `uv run python -c …` (pattern provato §1, utilizzabile). |
| W6 / R1 f6 — claim commit dossier | ✅ RISOLTO | Corpus punto 3: il grafo è mantenuto fresco dall'hook, «per il gate vale il contenuto del file, non il confronto con un commit specifico». GRAPH_REPORT `21344ade` = commit del brief ✓. |

**Perimetro:** tutti i delta osservati nel piano corrispondono a punti elencati nel Changelog (C6, regola 7 state.md, skip check_links, guardia+expected Task 13, disciplina Task 3, nota uv). Il resto del piano è coerente con la sintesi verbatim del round 1 (snippet, registri, expected, fixture). Nessuna modifica fuori perimetro rilevata. *Limite intrinseco:* senza il diff git eaefc58→21344ad la verifica di perimetro è per ispezione del corpus, non byte-diff (vedi rischi residui).

## 2. Desk-check C6 emendato — TUTTE le 12 fixture (simulazione a mente su `check_schema` + `check_meta_invariants` verbatim)

**6 VALIDE → zero errori (schema + C1–C8):**

| Fixture | Esito | Punti verificati |
|---|---|---|
| meta-create-intake | ✅ PASS | chapters [] → C1 `[] == range(1,1)` ✓; phase intake → C2/C4 esenti; stab assente mode create ✓; scope assente → C6 skip |
| meta-create-chapters | ✅ PASS | blocks+block_size 3 (if/then ✓); bible_approved=true → C2 ✓; numeri 1..3 + prefissi file ✓; user_review in phase chapters → C7 ✓; web false → C4 ✓ |
| meta-complete-bible | ✅ PASS | stab pending/pending presente (C5 richiede il blocco; phase bible ≠ chapters → nessun errore) ✓; imported×3, C8 ✓ |
| meta-revise-passes | ✅ PASS | scope [continuity,grammar,spelling] → idx [1,3,4] sorted ✓ (ramo revise); progress mirror ✓; gates bible ✓ |
| meta-restyle-final-review | ✅ PASS | **C6 restyle: uguaglianza esatta [style,continuity,grammar,spelling] ✓ — blocker R1 risolto**; awaiting=true/degraded=false → C3 ✓; gates bible+passes ✓; numeri 1..5, file pattern ✓; window 4 ∈ [2,10] ✓; blocks 5 ✓ |
| meta-revise-done | ✅ PASS | gates tutti true → C2 done ✓; degraded=true/awaiting=false → C3 ✓; scope subset ordinato idx [1,3,4] ✓; progress mirror ✓; notes string ✓ |

**6 INVALIDE → motivi di rifiuto:**

| Fixture | Motivo dichiarato | Desk-check |
|---|---|---|
| meta-invalid-bad-enum | schema (enum phase) | schema: `'drafting' is not one of [...]` ✓ — **ma scatta ANCHE C4** (vedi Finding R2-1) |
| meta-invalid-block-size | schema (minimum) | block_size 1 < 2 ✓, unico errore (phase intake → C4 esente; if/then soddisfatto: block_size presente) ✓ |
| meta-invalid-gates | C2 | phase passes + bible_approved=false → esattamente 1 errore C2; resto invariato ✓ |
| meta-invalid-file-number | C1 | cap.2 file `manuscript/03-echoes.md` → prefix mismatch C1 ✓; numeri ancora contigui, pattern schema ok, stabilization ok → unico errore ✓ |
| meta-invalid-flags | C3 | awaiting+degraded entrambi true → esattamente C3 ✓; scope restyle completo invariato → C6 muto ✓ (errore spurio R1 eliminato) |
| meta-invalid-scope | C6 (restyle equality) | scope [style,spelling] ⊆ PASS_ORDER → ramo restyle: ≠ lista pinnata → esattamente C6 ✓; progress coerente col set → mirror ok ✓ (errore spurio R1 eliminato) |

**Coerenza C6 ↔ resto del piano:** regola (7) state.md (Task 4 Step 6) ✓ · Task 9 Step 3 «`pass_scope` = [style, continuity, grammar, spelling] (C6)» ✓ · Task 11 «restyle = esattamente `style/voice → continuity → grammar → spelling`», create/complete = tutte, revise = subset dal revision-plan, stabilizzazione complete = solo structure+continuity su 1..M (gestita da C5, non da pass_scope) ✓ · Task 3 routing SKILL.md stessa coda ✓ · Global Constraint 8 / PASS_ORDER (chiavi interne) ✓ · spec matrice (iv) «stile (pilota come ancora) → continuità → grammatica → ortografia» + W4 ✓. Tutti allineati.

## 3. Finding Round 2

#### R2-1 — WARNING — Task 4 Step 4, fixture `meta-invalid-bad-enum.json` (motivo di rifiuto non esclusivo)

**Mismatch:** la fixture è dichiarata invalida via schema (enum `phase: "drafting"`), ma con `phase ≠ "intake"` e `flags.web_available: null` fa scattare **anche C4**: `flags.web_available must be true/false once past intake` (Task 4 Step 2: `if phase != "intake" and flags.get("web_available") is None`). La fixture è quindi rifiutata per il motivo dichiarato **più** un motivo non dichiarato — il desk-check «2 via schema, 4 via invarianti» del piano (Step 5) e la regola dossier §5 («rifiutata per il motivo dichiarato») non sono soddisfatte in forma esclusiva. Il round 1 lo aveva dato per passing basandosi sul log §1, che era schema-only (mini-schema, senza invarianti). **Impatto:** nessuno sugli expected dei run (`check_schema` richiede ≥1 errore per le invalide; Step 3 `FAIL — 12` e Step 5 `OK` restano esatti) → warning, non blocker. **Fix suggerita:** nella fixture bad-enum portare `"web_available": false` (delta di un campo, dentro il perimetro Task 4 Step 4; emendamento minore prima del dispatch). In alternativa, nota di esecuzione che dichiara il doppio motivo come noto.

#### Note non-finding (trasparenza, nessun'azione richiesta)

- **N1 — etichette W nel Changelog:** l'Amendamento 1 etichetta la disciplina inline-code «W3» e lo skip di `check_links` «W4», mentre nel dossier round 2 e nella tabella W1–W5 del piano quegli ID appartengono ai warning oracle (W3 = layout/description, W4 = coda passate). Il dossier round 2 usa la stessa convenzione shiftata («W4|finding 4»), quindi piano e dossier sono coerenti tra loro; è solo un'ambiguità di etichettatura rispetto alla tabella oracle. Contenuti tutti attuati e corretti.
- **N2 — refuso nel Changelog:** «(output locale del tool, **voi** link relativi non verificabili dal piano)» — evidente refuso per «con/i»; testo non prescritto, zero impatto meccanico.

## 4. Verifiche di regressione (delta adiacenti, sintesi)

- Task 4 Step 3 `FAIL — 12 problem(s)` ancora esatto: schema creato allo Step 1, 12 fixture mancanti, `check_schema` non duplica ✓.
- Task 2 Step 2 smoke `OK`: `check_links` ora salta `.git`/`node_modules`/`graphify-out`; sui .md di docs/ restanti l'assenza di link relativi rotti resta un'assunzione dichiarata dal piano (verifica 2026-11-25), non contraddetta dal corpus ✓.
- Task 3 Step 4 `OK` con disciplina inline-code: nessun hyperlink forward-reference → `check_links` muto ✓; description frontmatter una riga ~350 ≤ 1024, `name: book-forge` ✓ (invariato dal round 1).
- Nessun `python`/`pytest`/CLI jsonschema nudi in nessun task ✓; `format: "date"` solo annotation, nessun expected lo finge vincolo ✓; `.gitignore` Step 2 precede il primo `uv run` (Step 5) ✓; `uv sync --frozen` con `uv.lock` committato nello stesso Task 1 ✓; flag pandoc = §2, nessun task esegue pandoc ✓.
- Copertura spec→task invariata rispetto al round 1 (W1–W5, B1–B4 tracciati; nessun task orfano introdotto dall'amendamento).

## 5. Esito Round 2

**PASS con warning — blocker: 0, warning: 1** (R2-1, fixture bad-enum: doppio motivo di rifiuto schema+C4). Il blocker del round 1 è risolto e verificato su tutte le 12 fixture; W2–W6 attuati; perimetro dell'Amendamento 1 rispettato. Il dispatch può procedere; R2-1 va attuato come emendamento minore (un campo della fixture) o nota di esecuzione prima del worker del Task 4.

**Rischi residui:** (a) perimetro verificato per ispezione del corpus, non byte-diff git (il dossier non include il diff eaefc58→21344ad); (b) link relativi nei .md di docs/ fuori dal piano restano assunzione dichiarata, non provata nel dossier; (c) `npx skills add` e CI GitHub restano publish-time-only come dichiarato.