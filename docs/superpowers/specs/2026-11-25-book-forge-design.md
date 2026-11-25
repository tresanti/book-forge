# book-forge — Design Doc

Data: 2026-11-25 · Stato: **CONGELATA — FREEZE OK (oracle round 2)** · Nome working: `book-forge` (modificabile)

## Intento e perché

Una **skill pubblica** che accompagna chi non è uno scrittore ma ha una storia da raccontare o un manuale da scrivere: parte dall'idea (con appunti, concetti, materiale grezzo), porta l'agente a fare **le domande giuste** per estrarre il libro che l'utente ha in testa, poi orchestra la scrittura con subagenti e la correzione professionale (ortografia, grammatica, stile, continuità, struttura) fino al manoscritto finito esportabile in EPUB (importabile in Kindle Create) e .docx.

La stessa skill gestisce il caso **manoscritto esistente da correggere e sistemare**: la modalità è auto-rivelata al colloquio iniziale, non è una funzione separata.

Perché esiste: la ricerca sull'ecosistema (skills.sh, GitHub) ha mostrato pipeline complete solo in un harness Claude Code specifico e bloccante (tobyilee/book-writer), suite fiction-only con CLI dedicata (danjdewhurst/story-skills), o suite di planning senza esecuzione (wnsdy95/writer-skills). Nessuna skill harness-agnostic con colloquio d'ingresso, ciclo capitolo-per-capitolo con gate umano, e passate di correzione a subagenti su file singoli.

## Obiettivi

1. **Quattro lavori auto-rivelati al colloquio, stessa macchina di fondo**: (i) **creazione** da zero (romanzo o manuale); (ii) **completamento** di manoscritto parziale (i capitoli esistenti passano per diagnosi/revisione, i nuovi proseguono col ciclo a gate umano); (iii) **correzione** di manoscritto completo — anche scritto a mano prima della skill: niente fase di stesura, si entra da ingestione del file → diagnosi che **ricostruisce la bibbia dal manoscritto stesso** → validazione → piano di revisione → passate; (iv) **restyling**: libro finito ma l'utente vuole uno stile diverso → la nuova voce si estrae col colloquio; il vecchio libro rilascia SOLO canon/fatti/ledger (mai la vecchia style guide); al Gate 1 l'utente approva un **campione pilota riscritto** (1 capitolo o estratto) che fa da ancora few-shot per tutte le passate stile; poi la passata stile/voce gira per-file con subagenti in parallelo (testo + pilota + style guide per ognuno), sweep di continuità per il drift e gate finale.
2. **Colloquio d'ingresso per non-scrittori**: l'agente intervista una domanda alla volta, **nella lingua dell'utente** (rilevata dalla conversazione; la question bank come artefatto è in inglese), senza gergo editoriale (o col gergo spiegato in parole povere), fino ad avere: genere (fiction / saggistica pratica / narrative non-fiction), audience, promessa centrale, tono e voce, lingua del libro, lunghezza target, e — **domanda obbligatoria iniziale** — la modalità di validazione: un capitolo alla volta (default) oppure "valido a blocchi di N capitoli".
3. **Bibbia del libro come contratto**: un documento canon in plain markdown che ogni ruolo deve rispettare. Per fiction: premise, personaggi, mondo, archi, convenzioni. Per saggistica: concetti, promesse al lettore, TOC con logica, glossario terminologico. Per entrambi: style guide della voce, regole. **Per i lavori su manoscritto esistente la bibbia non esiste: la diagnosi la ricostruisce dal manoscritto** con uno sweep per capitolo (canon, glossario, ledger e una style guide che è **descrittiva** — com'è il libro ORA); la style guide **normativa** (come deve suonare) nasce dalla validazione dell'utente al Gate 1, che può accettare la voce attuale o indicare dove il libro NON è quello che voleva. la ricostruzione rileva anche le contraddizioni mentre le incontra.
4. **Materiale grezzo**: l'utente può fornire appunti/file/concetti (il colloquio parte da lì e fa meno domande) **oppure chiedere ricerche online** per informazioni e approfondimenti (se l'ambiente non offre accesso web, il Researcher lo dichiara subito e lavora sul solo materiale dell'utente, esplicitando il limite).
5. **Disciplina del diritto d'autore**: ogni testo riportato da fonti esterne porta SEMPRE la citazione della fonte; la riscrittura di un concetto con parole proprie avviene SOLO su richiesta esplicita dell'utente. Anche nella riscrittura la fonte resta tracciata in `research/` e nella sezione riferimenti del libro. Nessuna eccezione.
6. **Ciclo capitolo (creazione)**: il subagent drafter scrive il capitolo N (con bibbia + contratto del capitolo + handoff di continuità dai capitoli approvati) → **l'utente lo legge** → correzioni → **riscrittura immediata e ri-lettura dello stesso capitolo** → il capitolo si chiude solo all'approvazione → si passa al successivo. Con "blocchi di N": il gate umano arriva ogni N capitoli, stesso principio.
7. **Passate di correzione — la macchina condivisa tra i lavori**: `struttura → continuità → stile/voce → grammatica → ortografia` (**macro→micro**, standard editoriale: ogni passata che riscrive prosa passa PRIMA delle micro-correzioni, così la prosa riscritta arriva comunque verificata a valle; il piano di revisione seleziona il sottoinsieme che serve). Struttura e continuità operano **per capitolo in sequenza** contro il ledger — mai il libro intero in un contesto. Stile/voce, grammatica e ortografia sono passate **per-file** (un capitolo .md per subagent, parallelizzabili tra loro). Ogni passata produce un diff/registro verificabile. Il piano di correzione di un libro già scritto (anche a mano, pre-skill) e il restyling di un libro finito entrano da qui, senza mai passare dalla fase di stesura.
8. **Rilevamento e risoluzione delle contraddizioni tra capitoli**: il Continuity-checker confronta ogni capitolo con l'indice dei fatti del ledger — se il capitolo 12 contraddice il capitolo 4, la contraddizione emerge con **provenienza** ([cap.4] dice X, [cap.12] dice Y). La correzione si auto-applica SOLO se la bibbia validata risolve la contraddizione in modo univoco (e tocca solo i capitoli in errore); se il canon è ambiguo, il sistema si FERMA e chiede all'utente quale versione è canonica — il ledger non muta mai con scelte arbitrarie prima del gate umano.
9. **Gate finale indipendente, per-file**: un reviewer in contesto fresco (mai chi ha scritto) verifica il libro **capitolo per capitolo** (ognuno contro bibbia, ledger e registri — mai il libro intero in un contesto) e aggrega il rapporto finale; poi approvazione finale dell'utente. In modalità degradata inline: fine fase 3 → `meta.json` passa a `awaiting_fresh_session` e il pipeline SI FERMA — il gate gira in una sessione nuova; la self-review è ammessa solo con override esplicito dell'utente e viene marcata `degraded_non_independent` nel rapporto finale.
10. **Export**: pandoc → EPUB 3 compatibile Kindle Create + .docx opzionale. La skill **si ferma all'export**.
11. **Riprendibilità**: stato su disco; il progetto libro si può fermare per mesi e riprendere, la skill rilegge `meta.json` e capisce la fase.
12. **Portabilità totale**: funziona su pi (tool subagent), Claude Code (Task tool), e degrada a esecuzione inline dove non esistono subagenti.

## Non-goal

- Upload/pubblicazione su KDP (esistono skill dedicate: amazon-kdp ecc.)
- Cover design (esistono skill dedicate)
- Marketing, blurbs, biography, lancio
- Poesia, sceneggiature, libri ibridi testo-immagine (craft e formati diversi, v2 potrà valutarli)

## Anti-goal (fallimento anche se tecnicamente funziona)

- Scrivere capitoli senza passaggio dal gate umano di lettura/validazione
- Riprodurre testo protetto da diritto d'autore senza fonte
- Dipendere dai nomi di agenti custom di un ambiente specifico (scout/worker/reviewer di casa NON sono dipendenze)
- Formati di stato binari o lock-in di harness

## Vincoli

- Skill = plain markdown + prompt di ruolo; nessuna CLI obbligatoria per il nucleo della pipeline (fasi 0–4). Ingestione ed export, entrambi con check esplicito e messaggio chiaro: per l'**ingestione** dei .docx pandoc converte in markdown capitoli (con conferma utente dello split); per i .pdf serve un estrattore di testo dedicato — pandoc NON legge .pdf in input — con fallback a qualunque convertitore offra l'ambiente e dichiarazione del limite se assente; l'**export** EPUB 3/.docx (fase 5) resta pandoc. Senza pandoc il manoscritto markdown resta comunque completo e valido
- Artifacts pubblici in **inglese**; operatività su manoscritti in **qualsiasi lingua** (anche italiano)
- Economia di contesto: operare file-per-file, mai caricare il libro intero
- Distribuzione: repo GitHub pubblico installabile con `npx skills add <owner>/book-forge@book-forge` (ecosistema skills.sh) + clonabile per pi e Claude Code

## Approcci considerati

| # | Approccio | Esito |
|---|-----------|-------|
| 1 | **Skill orchestratrice nativa, harness-agnostic** (questa) | Scelto: copre esattamente i requisiti (colloquio, ciclo capitolo umano, passate a subagenti, export); costo: da costruire da zero; rischio complessità di orchestrazione mitigato da stato su disco e passate piccole |
| 2 | Portare book-writer (tobyilee) su pi | Scartato: documentazione coreana, harness Claude Code + Agent SDK, costo di adattamento superiore a una skill ex-novo |
| 3 | Comporre story-skills + colla custom | Scartato: fiction-only, CLI Node obbligatoria per progetto, formati pignoli; la colla restava comunque nostra |

## Decisioni decise dall'utente (come da conversazione)

1. Auto-rivelazione del lavoro al colloquio (creazione / completamento / correzione / restyling); il nome resta generico (vale il romanzo di domani e il manuale di oggi)
2. Niente stesura massiva parallela: ciclo capitolo con gate umano; "valido a blocchi di N" tra le domande iniziali obbligatorie
3. Riscrittura immediata + ri-lettura: il capitolo si chiude solo se approvato; le correzioni non si accumulano a fine lavorazione
4. Subagenti in correzione: uno specialista per passata, un file per volta, passate distinte — ordine originale ortografia→…→struttura (proposta del builder) **rivisto dal gate oracle (B1) in macro→micro**, vedi decisione 12; meccanismo per-file/sequenza invariato
5. Materiale grezzo fornito dall'utente oppure cercato online su richiesta
6. Copyright: fonte obbligatoria su ogni testo riportato; riscrittura del concetto su richiesta esplicita dell'utente
7. Export EPUB 3 (Kindle Create) + .docx opzionale; stop all'export, niente KDP upload
8. Skill pubblica in inglese, per tutti, indipendente dai flussi di agenti dell'autore
9. Gate della fase 3 = protocollo (b): registri diff controllati e campionati — ri-lettura integrale sempre disponibile quando l'utente vuole rileggere tutto
10. Contraddizioni tra capitoli: il sistema se ne accorge da sé — **raffinato dal gate oracle (B2)**: auto-correzione solo su canon univoco dalla bibbia validata; canon ambiguo → STOP e decisione dell'utente
11. Correzione di libro già scritto (anche a mano, pre-skill) e restyling di libro finito (subagenti per-file in parallelo) sono lavori di prima classe
12. [gate oracle round 1 — confermata dall'utente, 2026-11-25] Ordine passate = macro→micro: struttura → continuità → stile/voce → grammatica → ortografia

## Architettura

### Ruoli (prompt di ruolo spediti come file di riferimento, harness-agnostic)

| Ruolo | Dove gira | Compito |
|-------|-----------|---------|
| Interviewer | main agent inline (serve la conversazione con l'utente) | Colloquio d'ingresso, question bank per profilo genere |
| Researcher | subagent | Costruisce bibbia/materiali da appunti e fonti, ricerca online se richiesta, registra fonti |
| Drafter | subagent | Scrive il capitolo N con bibbia + contratto capitolo + handoff dei capitoli approvati |
| Copy-editor (× passata) | subagent | Una passata alla volta su un file: stile/voce (contro la style guide della bibbia), poi grammatica, poi ortografia — sempre in coda dopo le passate macro |
| Continuity-checker | subagent | Verifica contro bibbia e ledger di continuità |
| Structure-editor | subagent | Coesione capitolo e flusso libro |
| Final-reviewer | subagent in contesto fresco | Gate finale: bibbia rispettata, marker irrisolti, violazioni stile, rotture continuità. Mai il redattore dello stesso testo |

Dove non esiste tool subagent, i ruoli degradano a inline nello stesso contesto, stesso ordine — con due eccezioni protette: (1) il gate finale: fine fase 3 → `meta.json` = `awaiting_fresh_session`, stop hard, il gate gira in sessione nuova (self-review solo su override esplicito dell'utente, marcata `degraded_non_independent`); (2) il Researcher dichiara subito se non può cercare online e lavora sul solo materiale dell'utente.

### Formato del progetto libro su disco (source of truth)

```
mio-libro/
├── bible.md        # canon/contratto: premise, voce, glossario, regole; per-genere
├── outline.md      # TOC + contratto per ogni capitolo
├── manuscript/     # 01-titolo.md, 02-titolo.md... (un file per capitolo)
├── continuity/     # (a) facts-index.md: entità/fatti/promesse con provenienza [cap.XX]; (b) window/: gli ultimi K handoff approvati
├── research/       # materiale grezzo, fonti con URL/data, note
├── exports/        # libro.epub, libro.docx
└── meta.json       # fase pipeline, genere, lingua, modalità validazione, progresso capitoli
```

### Pipeline di fasi

```
Fase 0 — Colloquio (inline)
  domande → rileva modalità (nuovo/esistente), genere, audience, promessa,
  tono, lingua, blocchi-N → raccoglie/carica materiale grezzo
     ↓
Fase 1 — Bibbia + outline (o Ricostruzione bibbia + piano revisioni per esistente)
  creazione: subagent costruisce → GATE 1: approvazione utente di bibbia+outline
  esistente: ingestione (docx→md per capitoli) → sweep diagnostico per capitolo
  che ricostruisce bibbia+ledger e rileva contraddizioni → GATE 1: l'utente
  valida la bibbia ricostruita ("questo è il libro che hai scritto?")
  e approva il piano di revisione
     ↓
Fase 2 — Ciclo capitoli (solo lavori (i) e (ii): creazione o completamento)
  drafter scrive N → utente legge → le correzioni tornano al DRAFTER che
  riscrive immediatamente (round-trip; il main agent orchestra soltanto) →
  ri-lettura → CHIUSO ad approvazione → N+1 (o ogni N in modalità blocchi)
     ↓
Fase 3 — Passate di correzione (macchina condivisa: la correzione di un libro
  esistente E il restyling di un libro finito ENTRANO QUI, senza fase 2)
  struttura → continuità → stile/voce → grammatica → ortografia (macro→micro)
  struttura/continuità: per capitolo in sequenza contro il ledger
  stile/grammatica/ortografia: per-file, subagenti in parallelo
  contraddizioni: auto-fix SOLO su canon univoco (solo capitoli in errore);
  canon ambiguo → STOP + decisione utente → registro diff
  GATE fase 3 = protocollo (b): registri diff controllati e campionati,
  ri-lettura integrale sempre possibile a scelta di chi scrive
     ↓
Fase 4 — GATE FINALE: reviewer fresco, verifica per-file + rapporto aggregato,
  approvazione utente (inline: stop awaiting_fresh_session → sessione nuova)
     ↓
Fase 5 — Export: pandoc → EPUB 3 (Kindle Create) + .docx opzionale
```

### Profili genere (pilotano template bibbia, question bank del colloquio e criteri di valutazione)

- **fiction**: canon personaggi/mondo/archi, POV, payoff
- **practical non-fiction** (manuale/how-to): trasformazione del lettore, promesse, TOC didattica, esercizi
- **narrative non-fiction** (memoir/saggio narrativo): struttura reale + tessuto narrativo

### Matrice Fasi × Lavori (routing esplicito)

| Fase | (i) creazione | (ii) completamento | (iii) correzione | (iv) restyling |
|------|---------------|--------------------|------------------|----------------|
| 0 Colloquio | sì | sì | sì | sì |
| 1 Bibbia/outline | sì (nuova) | ricostruzione sui capitoli 1..M + **stabilizzazione di 1..M PRIMA di scrivere M+1** (= ricostruzione validata + passate struttura e continuità sui 1..M; stile/grammatica/ortografia restano alla fase 3 sull'intero libro) | ricostruzione + piano revisione → GATE 1 | ricostruzione SOLO canon/fatti/ledger + nuova voce + **pilota riscritto** → GATE 1 |
| 2 Ciclo capitoli | 1..N | da M+1 | — | — |
| 3 Passate | post-stesura | post-stesura | **lavoro principale** | stile (pilota come ancora) → continuità → grammatica → ortografia |
| 4 Gate finale | sì | sì | sì | sì |
| 5 Export | sì | sì | sì | sì |

## Cosa resta al builder (decisioni libere)

- Question bank del colloquio per profilo (una domanda per volta, per non-scrittori)
- Template bibbia per profilo (campi minimi vs opzionali)
- Wording dei prompt di ruolo (file references/roles/*.md)
- Formato ledger di continuità (campi, aggiornamento dopo ogni capitolo approvato)
- Manifesto passate: routine di ogni specialista (cosa cerca, cosa tocca, cosa non tocca, come registra il diff)
- Dettagli pandoc: comando, metadati EPUB, naming export
- Layout repo per skills.sh e istruzioni installazione pi/Claude Code
- Euristica lunghezza capitolo dal genere e dal target
- `meta.json`: schema esatto e regole di avanzamento fase

### Ingresso per manoscritto esistente — riepilogo del percorso (es. .docx)

```
  1. ingestione file → split proposto → l'utente CONFERMA i confini capitolo
  2. sweep diagnostico per capitolo: ricostruzione bibbia + ledger
     (facts-index con provenienza + finestra handoff), contraddizioni rilevate
  3. GATE 1: l'utente valida bibbia ricostruita + piano revisione
  4. passate (macchina condivisa fase 3, macro→micro) → gate (b) → export
```

## Esito builder-check (2026-11-25) — chiamate del builder documentate

1. Pandoc: prerequisito solo fase 5, check + fail esplicito; nucleo pipeline senza CLI
2. Continuità/struttura: per capitolo in sequenza contro il ledger compresso, mai libro intero
3. Manoscritto parziale: terzo stato auto-rivelato (non pipeline separata)
4. Copyright: allineato l'obiettivo 5 alla decisione utente 6 (citazione sempre; riscrittura solo su richiesta)
5. Gate finale inline: sessione nuova obbligata, fallback self-review strutturata
6. Senza web: Researcher dichiara il limite e lavora sul materiale utente
7. Colloquio: nella lingua dell'utente (question bank artefatto inglese)
8. Riscrittura in fase 2: round-trip del drafter, main agent orchestra
9. Bibbia ricostruita dal manoscritto per i lavori (iii)/(iv): sweep diagnostico estrae stile/glossario/canon/ledger, l'utente la valida al Gate 1 (buco esposto dall'utente sul caso .docx, 2026-11-25)
10. Packaging: UNA sola skill con progressive disclosure (SKILL.md sottile = macchina a stati + dispatch; conoscenza per fase in references/: interview, bible-templates, roles, passes, export). Criterio di uscita: una passata diventa skill standalone solo quando risulta utile fuori dal libro
11. Ingestione .docx/.pdf: adapter pandoc-primario con fallback ambiente, dichiarazione esplicita se assente

## Gate oracle — round 1 (2026-11-25)

**Verdetto: FREEZE BLOCCATO** — 4 blocker, 3 warning; fix dell'autore applicati il giorno stesso:

- **B1 ordine passate**: invertito in macro→micro (struttura → continuità → stile/voce → grammatica → ortografia). La decisione utente #4 (ordine micro→macro) era una proposta errata del builder: le passate che riscrivono prosa invalidavano le micro-correzioni precedenti e la prosa riscritta arrivava al gate finale non verificata. → obiettivo 7, fase 3, decisione 4 (annotata) + nuova decisione 12
- **B2 ledger e auto-correzione cieca**: continuity/ ora = (a) indice strutturato di fatti/entità/promesse con provenienza [cap.XX] + (b) finestra scorrevole degli ultimi K handoff; auto-fix solo su canon univoco dalla bibbia validata (solo capitoli in errore); canon ambiguo → STOP utente. → obiettivo 8, formato su disco, decisione 10 (raffinata)
- **B3 routing dei 4 lavori**: matrice Fasi×Lavori esplicita; (ii) stabilizza 1..M prima di M+1; (iii) style guide estratta = descrittiva, normativa al Gate 1; (iv) il vecchio libro rilascia solo canon/fatti/ledger, pilota riscritto approvato come ancora few-shot PRIMA del parallelo. → obiettivi 1(iv), 3, matrice nuova, fase 2
- **B4 gate finale vs vincolo contesto**: verifica per-file con rapporto aggregato (mai libro intero); inline = stop `awaiting_fresh_session` su meta.json + override utente marcato `degraded_non_independent`. → obiettivo 9, ruoli, fase 4

**Warning registrati per la fase piano:** W1 la SKILL.md deve iniettare i path dei prompt di ruolo ai subagenti e rileggere `references/<fase>.md` a ogni resume da meta.json; W2 pandoc NON legge .pdf in input (serve estrattore dedicato + dichiarazione del limite) e lo split capitoli post-ingestione va confermato dall'utente; W3 layout skills.sh: `skills/book-forge/SKILL.md` con description circoscritta al dominio libro/manoscritto.

## Gate oracle — round 2 (2026-11-25)

**Verdetto finale: FREEZE OK.** B1, B2, B3, B4 tutti RISOLTI; nessun nuovo blocker introdotto dai fix. Trasparenza verso l'utente riconfermata (decisioni 4/10 distinguono mandato utente e correttivi oracle; decisione 12 confermata dall'utente).

**Warning per la fase piano (non bloccanti, da attuare nel piano):**
- **W1**: la SKILL.md inietta i path `references/roles/*.md` nei prompt dei subagenti e rilegge `references/<fase>.md` a ogni resume da `meta.json`
- **W2**: .docx→pandoc, .pdf→estrattore dedicato (vedi Vincoli); conferma utente dello split capitoli post-ingestione
- **W3**: layout `skills/book-forge/SKILL.md` per skills.sh/pi/Claude Code, con `description` circoscritta al dominio libro/manoscritto
- **W4**: per (iv) la fase 3 include la coda `grammatica → ortografia` dopo `stile → continuità` (matrice aggiornata); per (ii) definito il sottoinsieme passate della stabilizzazione 1..M (matrice aggiornata)
- **W5**: Final-reviewer = dispatch di subagent freschi per-capitolo + aggregazione dei soli report (mai un unico subagent che accumula N capitoli in contesto); `facts-index.md` va risincronizzato dopo modifiche di struttura/canon in fase 3

## Domanda ancora aperta per l'utente

Risolta in conversazione: **protocollo (b)** per il gate della fase 3 (registri diff + campionamento, ri-lettura integrale sempre disponibile). Nella stessa risposta l'utente ha esteso il design con due lavori di prima classe (correzione di libro già scritto anche a mano; restyling di libro finito con subagenti per-file in parallelo) e il protocollo contraddizioni tra capitoli — integrati negli obiettivi 1, 7, 8, nelle decisioni 9–11 e nel pipeline.
