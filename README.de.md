# irsanai-nexus-repo — Repository Intelligence Plattform (DE)

IRSAN AI Nexus analysiert GitHub-Repositories und liefert ein einheitliches Intelligence-Resultat (Sprachen, Repo-IQ, Security-Indikatoren und relevante Dateiauszüge).

## Highlights
- FastAPI-Backend mit `/health`, `/analyze` und `/reports`.
- Top-File-Snippets überspringen Binärdateien für besser lesbare Analyse-Ausgaben.
- Sicheres GitHub-Klonen mit URL-Validierung.
- Windows-robustes Cleanup für gesperrte `.git/objects/pack/*`-Dateien.
- Leichte Insight-Console unter `/` mit KPI-Karten, Report-Vergleich, Delta-Heatmap und Report-Browser.
- GitHub-Pages-fähige statische Seite aus `docs/`.

## Schnellstart (lokal)
```bash
git clone https://github.com/irsanai/irsanai-nexus-repo
cd irsanai-nexus-repo
chmod +x scripts/setup.sh && ./scripts/setup.sh
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

Dann öffnen:
- API: `http://127.0.0.1:8000/health`
- UI: `http://127.0.0.1:8000/`


## Schnellstart (Windows / PowerShell)
```powershell
git clone https://github.com/irsanai/irsanai-nexus-repo
cd irsanai-nexus-repo
./scripts/setup.ps1
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

> Hinweis: `&&` und `source` sind Bash-Befehle und funktionieren in PowerShell nicht.


## Schnellstart (Docker)
```bash
# produktionsnaher Container
docker compose -f docker/docker-compose.yml up --build -d backend

# UI öffnen
start http://127.0.0.1:8000/

# Dev-Profil mit Reload auf Port 8001
docker compose -f docker/docker-compose.yml --profile dev up --build backend-dev
```

Docker-Services persistieren Workdir und Reports über Named Volumes (`repo_work`, `reports`).

## API-Nutzung für Analyse
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/psf/requests","save_report":true}'
```

Letzte Reports auflisten:
```bash
curl http://127.0.0.1:8000/reports
```

Zwei Reports vergleichen (Delta):
```bash
curl "http://127.0.0.1:8000/reports/compare?id1=<report_id_1>&id2=<report_id_2>"
```

Einen Report per ID abrufen:
Reports werden standardmäßig unter `reports_output/` gespeichert (anpassbar über `REPORTS_DIR`).

```bash
curl http://127.0.0.1:8000/reports/<report_id>
```

Einen lesbaren HTML-Report öffnen:
```bash
start http://127.0.0.1:8000/reports/<report_id>/html
```

## Windows-Stabilität
Wenn zuvor `WinError 5` beim Löschen auftrat, enthält das Repo jetzt:
1. Ein temp-basiertes Standard-`work_dir` (`tempfile.gettempdir()`), und
2. Retry + chmod-basiertes Cleanup.

Optional in `.env` überschreiben:
```dotenv
WORK_DIR=./repo_work
```

## GitHub Pages
Workflow unter `.github/workflows/pages.yml`. Nach Aktivierung von GitHub Pages (Quelle: GitHub Actions) wird bei Push auf `main` automatisch `docs/index.html` deployed.

Um die gehostete UI mit deiner API zu verbinden: `?api=https://dein-api-host` an die URL anhängen.

## Preflight-Vergleich lokal/remote
Erzeuge in PyCharm/lokal ein deterministisches JSON-Inventar und teile es für Delta-Analyse:
```bash
python scripts/preflight_inventory.py --output preflight.local.json
```

## Integrations-Audit
Führe ein gewichtetes Integrations-Audit aus (Architektur, Betrieb, Qualität, UX):
```bash
python scripts/integration_audit.py
```


## Produkt-Roadmap & Status-Tracking

### Status-Legende
- ✅ Erledigt
- 🟡 In Arbeit
- ⚪ Geplant
- 🔁 Laufend/iterativ

### Aktueller Integrations-Snapshot (Delta-Sicht)
- **Vor der letzten Phase:** Analyze-API + persistente Reports + Compare + HTML-Report + Insight-Console-Basis.
- **Jetzt (aktueller gemergter Stand):** Delta-Heatmap im Compare-Workflow, Compare-Endpoint vorhanden, Docker-Runtime/Dev-Profil angeglichen, Integrations-Audit bei **100/100 (A)**.
- **Nächstes Ziel:** von JSON-zentrierter Inspektion zu hochdimensionaler Insight-Navigation (2.5D-Graph + Drilldowns), bei stabilen/additiven APIs.

### Hauptphasen der Roadmap
| Phase | Ziel | Status | Notiz |
|---|---|---|---|
| A | Insight-Cockpit für Nicht-Coder | ✅ | KPI-Karten, Report-Browser, Compare + Delta-Heatmap sind vorhanden. |
| B | 2.5D-Relationship-Graph | 🟡 | Nächster Implementierungsschritt; Start mit Node/Edge-Projektion in 2D/2.5D. |
| C | Human-in-the-loop LLM-Workspace | ⚪ | Prompt-Builder + Response-Ingest + Memory nach Graph-Basis geplant. |

### Haupt-/Nebentasks mit Status
| Track | Sub-Task | Status | Nutzen |
|---|---|---|---|
| Reports | Persistente Report-Speicherung + Listing | ✅ | Ermöglicht Historie und reproduzierbare Analysen. |
| Reports | Report-Compare-API (`/reports/compare`) | ✅ | Ermöglicht Delta-Denken statt isolierter Snapshots. |
| Reports | HTML-Report-View (`/reports/{id}/html`) | ✅ | Ergebnisse leicht teilbar für nicht-technische Stakeholder. |
| UX | Insight-Console mit KPI-Karten | ✅ | Schnelles Verständnis des Repo-Zustands. |
| UX | Delta-Heatmap-Visualisierung | ✅ | Schnelle visuelle Interpretation von Trendrichtung/-stärke. |
| UX | Timeline-View der Report-Entwicklung | 🟡 | Teilweise via Recent Reports vorhanden; eigene Timeline-UI noch offen. |
| Graph | Datenmodell für Nodes/Edges (Dateien, Risiken, Metriken) | ⚪ | Voraussetzung für hochdimensionale Navigation. |
| Graph | 2.5D-Canvas mit Zoom/Pan/Filter | ⚪ | Brücke zu immersiver Interaktion ohne sofortige Full-3D-Komplexität. |
| AI-Loop | Prompt-Workbench (provider-neutral) | ⚪ | Unterstützt externen LLM-Augmentation-Workflow. |
| AI-Loop | LLM-Response-Ingest + semantischer Diff | ⚪ | Macht aus One-shot-Ausgaben iteratives Intelligence-Wachstum. |
| Plattform | Pflege des Integrations-Audits | 🔁 | Hält Roadmap-Lieferungen architektonisch im Einklang. |
| Plattform | CI + Security-Checks (`ruff`/`pytest`/`bandit`) | 🔁 | Verhindert Regressionen bei wachsender UX-Komplexität. |
| Plattform | Docker-Parität (Runtime + Dev-Profil) | ✅ | Container-User erhalten denselben Kern-UX/API/Report-Stand. |

### Leitplanken für die nächsten Schritte
1. APIs möglichst additiv und nicht-brechend erweitern.
2. `docs/index.html` stets mit `frontend/index.html` synchron halten (Pages-Parität).
3. Report-Schema versionieren, bevor Graph-/Prompt-Memory-Payloads erweitert werden.
4. Für jedes Roadmap-Inkrement Integrations-Audit + Tests erneut ausführen.
