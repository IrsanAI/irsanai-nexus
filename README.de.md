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
