# irsanai-nexus-repo — Repository Intelligence Plattform (DE)

IRSAN AI Nexus analysiert GitHub-Repositories und liefert ein einheitliches Intelligence-Resultat (Sprachen, Repo-IQ, Security-Indikatoren und relevante Dateiauszüge).

## Highlights
- FastAPI-Backend mit `/health` und `/analyze`.
- Sicheres GitHub-Klonen mit URL-Validierung.
- Windows-robustes Cleanup für gesperrte `.git/objects/pack/*`-Dateien.
- Leichte Web-UI unter `/` für direkte Analysen.
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

## API-Nutzung für Analyse
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/psf/requests"}'
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
