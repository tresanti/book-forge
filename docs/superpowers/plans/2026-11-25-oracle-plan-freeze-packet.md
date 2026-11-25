# Packet oracle — freeze del piano book-forge

Data: 2026-11-25 · Modalità: **freeze del piano** (Livello 3, gate obbligatorio pre-dispatch) · Repo: C:/Libri/book-forge

## Regole del verdetto

- Sei single-shot: il corpus qui sotto è l'input; non esplorare liberamente la macchina né il repo oltre i file elencati. La raccolta è già fatta (raccolta = dossier/orchestratore; il giudizio è tuo).
- Solo i finding **blocker** impediscono il freeze del piano. I finding **warning** tornano all'autore come emendamento (come già accaduto per Amendamento 1 e 2), senza bloccare il dispatch una volta attuati.
- Loop bounded: max 2 giri di fix autore↔oracle, poi escalation all'utente.
- Se un'API esterna citata ti sembra sospetta, le evidenze verbatim raccolte dall'orchestratore sono nel dossier plan-validator (corpus §5): affidati a quelle; apri file solo dentro il corpus.
- Verdetto finale: **FREEZE OK** / **FREEZE BLOCCATO** + finding numerati (severità, evidenza path+sezione, fix) + un paragrafo di rischi residui che accetti.

## Corpus (leggi questi, null'altro)

1. `docs/superpowers/specs/2026-11-25-book-forge-design.md` — spec CONGELATA (FREEZE OK, oracle round 2, W1–W5). **Autorità: NON produrre finding su di essa** — è già approvata; l'oggetto del giudizio è il piano rispetto a lei.
2. `docs/superpowers/specs/2026-11-25-book-forge-oracle-dossier.md` — dossier del freeze della SPEC (cronistoria decisionale, builder-check, gate oracle round 1/2): cosa era già stato approvato e con quali correttivi.
3. `docs/superpowers/plans/2026-11-25-book-forge-skill.md` — il piano di implementazione (15 task), **con Amendamento 1 e 2 applicati** (Changelog in coda).
4. `docs/superpowers/plans/2026-11-25-plan-validator-report.md` — lint meccanico: Round 1 BLOCKED (1 blocker + 5 warning) → Amendamento 1 → Round 2 PASS con warning (R2-1 + N1/N2) → Amendamento 2. Zero blocker aperti.
5. `docs/superpowers/plans/2026-11-25-plan-validator-dossier.md` — evidenze verbatim d'ambiente usate dal lint (uv 0.13.5/CPython 3.13.17 + jsonschema draft 2020-12 provati con scratch; flag pandoc verificati sui documenti ufficiali; regole di discovery/frontmatter di pi 1.6.0).
6. `graphify-out/GRAPH_REPORT.md` — grafo del repo, mantenuto fresco dall'hook post-commit a ogni commit.

## Cronistoria compatta

- Spec congelata 2026-11-25 (oracle round 1: FREEZE BLOCCATO per B1–B4; fix applicati; round 2: FREEZE OK, W1–W5 per la fase piano).
- Piano: 15 task, struttura `skills/book-forge/{SKILL.md, references/*, references/roles/*}`, harness dev uv+jsonschema (`tests/check.py` con registri di contratto), `meta.schema.json` + invarianti C1–C8 + 12 fixture, albero progetto utente esteso (passes/, reports/, pilot.md, revision-plan.md, book.yaml).
- plan-validator round 1: BLOCKED — C6 imponeva un solo ordine macro→micro a tutte le modalità, rendendo insoddisfacibile lo scope restyle pinnato dalla spec → **Amendamento 1**: contratti C6 per modalità (revise = subset ordinato; restyle = [style, continuity, grammar, spelling] voce prima; create/complete = ordine completo) + W2–W6 del round 1.
- plan-validator round 2: PASS con warning — R2-1 (fixture bad-enum con doppio motivo di rifiuto) + N1/N2 → **Amendamento 2**. Meccanica chiusa: nessun blocker aperto.

## Diff degli emendamenti (perimetro)

- `eaefc58 → 21344ad` (Amendamento 1): piano (C6, regola 7 state.md, skip graphify-out in check_links, guardia anti-duplicato check_role_paths, expected Task 13, disciplina inline-code Task 3, nota uv run, Changelog) + report round 1 + dossier round 2. 3 file, +109/−17.
- Amendamento 2 (commit corrente): piano — fixture bad-enum `"web_available": false` + nota, chiarimento N1, refuso N2.

## Macro-questioni per il tuo giudizio (architetturale — il lint meccanico è già passato)

1. **Deriva dal freeze della spec?** Il piano introduce pezzi NON esplicitati nell'architettura congelata, tutti riconducibili ai punti liberi ("Cosa resta al builder"): (a) harness dev `tests/check.py` con registri di contratto (headers/substring esatte, fixture, check frontmatter/link/role-path) girato in CI — separato dal runtime della skill (utente senza dipendenze); (b) `meta.schema.json` + invarianti C1–C8 come contratto machine-checkable del formato su disco; (c) estensioni dell'albero progetto utente là dove la spec mostrava il nucleo (passes/ con registry per passata e contradiction-NN.md, reports/final-review/ per capitolo + aggregato, pilot.md, revision-plan.md, book.yaml); (d) manifesto passate splittato: passes.md = orchestrazione (ordine, ambiti, contraddizioni, resync, gate (b)); routine per specialista nei 6 role file. Giudica: deriva da concepire diversamente, o attuazione legittima dei punti liberi? Serve re-freeze di qualche pezzo?
2. **Vincoli cardinali intatti?** Economia di contesto (mai il libro intero; un capitolo per subagent; structure/continuity sequenziali contro il ledger), gate umani hard (invariante C2, ciclo capitolo con ri-lettura), contraddizioni B2 (auto-fix SOLO canon univoco e solo capitoli in errore; STOP su ambiguo), gate finale B4/W5 (fresh session, per-capitolo, aggregazione dei soli report, degraded marcato), stop-all'export. Il piano li attua senza attenuazioni nascoste in qualche task?
3. **W1–W5 attuati senza regressioni su B1–B4?** La tabella «Warning oracle → task» del piano dichiara la copertura e ogni warning ha un ancoraggio meccanico (substring/fixture/check). Ti risultano punti in cui l'attuazione piega o erra?
4. **Frammentazione e ordine dei task.** 15 task, ciascuno fail→implement→pass→commit sull'harness. Giunzioni delicate volutamente scelte: Task 3 (SKILL.md) usa gli enum pinnati nel Task 4 (i valori sono scritti nel piano stesso, quindi consumabili in anticipo); i role file arrivano dopo le reference che li citano (inline code + check_role_paths al Task 13 chiude il cerchio); Task 4 Step 3 expected basato su file creato nello Step 1. Giudica: fragilità architetturale accettabile o rischio di dispatch fallito?
5. **Rischi residui del lint:** perimetro Amendamento 1 verificato per ispezione e non byte-diff; link relativi fuori dal piano = assunzione dichiarata; `npx skills add` + CI provati publish-time-only. Alcuno è architetturalmente rilevante per il freeze?
6. **Scelte di dettaglio libere fissate dal piano** (giudizio rapido di coerenza col mandato): euristica lunghezza capitolo (fiction 2,000–4,000 parole / target 80–90k; practical 3,000–5,000 / 40–60k; narrative 2,500–4,500 / 55–75k); `continuity_window` default 3 (2–10) con pruning dei file oltre K; registro diff per passata con campione before→after; pilota come ancora few-shot incluso in OGNI dispatch di stile (restyle); regole di transizione meta.json (solo orchestratore scrive; non si retrocede mai dai gate senza decisione utente); descrizione SKILL.md circoscritta al dominio libro/manoscritto.

## Escalation

- Blocker → l'autore corregge il piano (Amendamento 3) e si rilancia il gate (max 2 giri), poi escalation all'utente.
- Warning → ammendamento pre-dispatch (i worker del task colpito ricevono brief aggiornato).

---

## ROUND 2 — istruzioni (verifica dell'Amendamento 3)

- **Cronistoria aggiornata**: round 1 = FREEZE BLOCCATO (3 blocker + 4 warning, finding O1–O7 nel corpus §4); l'autore ha applicato l'**Amendamento 3** (Changelog in coda al piano, con impatto-fixture dichiarato a zero). Corpus invariato + questo verdetto: `docs/superpowers/plans/2026-11-25-oracle-plan-freeze-verdict.md` (aggiunto al corpus come punto 7).
- Verifica per il round 2:
  1. **O1 (C8/routing)**: C8 emendato (`phase not in ("intake","bible") or bible_approved`) — desk-check contro le 12 fixture (esito invariato); routing `phase × work_mode` in SKILL.md Task 3 (bible → bible.md | ingest.md | reconstruction.md) + regola 9 di state.md + redirect in bible.md Task 7 + substring `references/ingest.md`.
  2. **O2 (mode complete)**: reconstruction.md — sweep che estrae sintesi purpose/beat → `outline.md` sui capitoli importati + window degli ultimi K capitoli; Gate 1 complete/revise: style guide descrittiva → NORMATIVA con la validazione utente; complete: al Gate 1 si approvano i contratti M+1..N e DOPO la stabilizzazione si registrano M+1..N (`planned`, `written`) prima di `phase: "chapters"`; bible.md Gate 1: init capitoli 1..N per create; drafting.md Closing: ultimo `approved` → `phase: "passes"` + init `pass_scope`/`pass_progress` per C6.
  3. **O3 (race registri)**: frammenti `passes/registry-<pass>/ch-NN.md` scritti dai subagenti paralleli; registro della passata `aggregated by the orchestrator` a fine passata (output contract copy-editor allineato).
  4. **O4–O7 (warning)**: sliding window per passata + sezione `stabilization (phase 1)` nei registri; popolazione PROVISIONAL pre-Gate-1 di facts-index + `research/reconstruction-notes.md` in input a ogni dispatch Duty B; ingest senza lettura integrale del raw; pilota restyle eseguito da copy-editor; state.md regole 3/8 estese (sessione fresca riconosciuta + retrocessione controllata + batching inline) + `nor its Phase 3 editor`; C5 esteso a tutte le fasi post-stabilizzazione; C7 vieta `planned` da `passes` in poi; guardia STOP-file in passes.md; Note di esecuzione: inline-code GLOBALI + STRICTLY SEQUENTIAL; fallback stateless in drafting.md; slug ASCII/translitterazione; regex language allargata; README con `@book-forge` verbatim della spec.
  5. **Perimetro**: nessuna modifica al piano fuori dai punti elencati nel Changelog dell'Amendamento 3; 15 task invariati; nessun re-freeze della spec richiesto (il tuo round 1 lo conferma).
  6. ** re-giudizio**: conferma o confuta le conclusioni residuali del round 1 su Q2 (vincoli cardinali) e Q3 (W1–W5 vs B1–B4) alla luce dei fix.
- Esci con: verdetto round 2 (**FREEZE OK** / **FREEZE BLOCCATO**) + conteggio finding residui (blocker|warning) + paragrafo di rischi residui accettati.
