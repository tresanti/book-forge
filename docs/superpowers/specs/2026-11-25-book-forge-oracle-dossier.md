# Dossier oracle — freeze spec "book-forge" (2026-11-25)

**Modalità:** freeze spec · **Verdetto richiesto:** blocker / warning / ok, single-shot · **Bound:** max 2 giri di fix, poi escalation utente.

## Il progetto in una frase

Skill pubblica, harness-agnostic (pi / Claude Code / ecosistema skills.sh), che porta un non-scrittore dall'idea (o dal manoscritto già scritto) al libro finito: colloquio d'ingresso → bibbia → scrittura capitolo-per-capitolo con gate umano → passate di correzione via subagenti → gate finale indipendente → export EPUB 3/.docx.

## Artefatti del dossier

| Artefatto | Percorso |
|---|---|
| Spec da giudicare | `docs/superpowers/specs/2026-11-25-book-forge-design.md` (workspace `C:/Libri/DominareIlTuoLavoroConAI`) |
| Grafo del workspace | `graphify-out/GRAPH_REPORT.md` (16 nodi, 15 comunità — workspace quasi vuoto: solo la spec e questo dossier) |
| Diff/versioni | n/a — prima stesura (storia delle revisioni: sezione "Esito builder-check" in coda alla spec) |
| Codice esistente | nessuno — progetto greenfield, non esistono ancora file di codice |

## Cronistoria decisionale (per contesto, senza dover esplorare)

1. Ricerca prior art: pipeline completa esiste solo in harness Claude Code lock-in (tobyilee/book-writer, coreano, Agent SDK); fiction-only con CLI (story-skills); planning senza esecuzione (wnsdy95/writer-skills). Gap confermato per una skill harness-agnostic completa.
2. Utente ha scelto l'opzione A (skill orchestratrice nativa) scartando il porting di book-writer e la composizione di skill esistenti.
3. Builder-check (subagent indipendente) ha trovato 4 contraddizioni e 5 buchi — tutti risolti (sezione "Esito builder-check" della spec).
4. Utente ha esteso i requisiti nel closed-loop: 4 lavori di prima classe (creazione/completamento/correzione/restyling), contraddizioni tra capitoli con correzione di entrambi, gate fase 3 = protocollo (b) diff-registri + campionamento.
5. Buco esposto dall'utente (manoscritto .docx pre-esistente senza bibbia) → chiuso con la ricostruzione della bibbia dal manoscritto (sweep diagnostico + validazione utente al Gate 1).
6. Packaging deciso (chiamata del builder, approvata dall'utente): UNA sola skill con progressive disclosure — SKILL.md sottile (macchina a stati + dispatch), conoscenza per fase in `references/` (interview, bible-templates, roles, passes, export).

## Macro-questioni architetturali su cui si chiede giudizio

1. **Macchina a stati su disco + progressive disclosure**: la coppia SKILL.md sottile + references/ regge la portabilità tra harness con semantiche di loading diverse (pi skills, skills.sh, Claude Code skills), o c'è un rischio strutturale di contexts divergenti non modellati?
2. **Bibbia ricostruita dal manoscritto** (lavori iii/iv): lo sweep diagnostico per capitolo che estrae stile/glossario/canon/ledger è architetturalmente solido, o sottovaluta il problema che la "voce" di un libro non è semplicemente estraibile per capitoli?
3. **Gate finale indipendente senza subagenti**: in modalità degradata inline la promessa "reviewer in contesto fresco, mai chi ha scritto" si mantiene? La mitigazione scelta (sessione nuova richiesta all'utente, fallback self-review strutturata) è sufficiente o è una promessa che si rompe al primo contatto con la realtà?
4. **Ledger compresso come stato di continuità**: sufficiente per rilevare contraddizioni tra capitoli distanti in libri lunghi (40+ capitoli), o serve modellare esplicitamente la finestra di contesto del Continuity-checker?
5. **Singola skill vs suite nel packaging**: la scelta regge per tutti e tre i canali di distribuzione, o skills.sh (install per-skill) premia strutturalmente la forma-suite rendendo il monolite con references un cittadini di serie B?
6. **Quattro lavori, una macchina**: l'unificazione di creazione/completamento/correzione/restyling in una sola pipeline a fasi riusa un rischio di complessità non gestita (la fase 3 diventa un coltellino svizzero che nessuno domina)?

## Regole del verdetto

- Solo i finding **blocker** impediscono il freeze (e richiedono fix + nuovo giro, max 2).
- I warning si registrano come note per la fase piano.
- Non esplorare il workspace: tutto ciò che serve è in questo dossier e nella spec.
