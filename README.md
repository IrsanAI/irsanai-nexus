# irsanai-nexus-repo — Repository Intelligence Platform (EN)

IRSAN AI Nexus analyzes GitHub repositories and returns a unified intelligence payload (languages, repo IQ, security indicators, and context-rich file snippets).

## Highlights
- FastAPI backend with `/health`, `/analyze`, and `/reports` endpoints.
- Top-file snippets skip binary files to keep analysis output readable.
- Safe GitHub cloning with URL validation.
- Windows-friendly cleanup handling for locked `.git/objects/pack/*` files.
- Lightweight web UI at `/` for direct analysis runs.
- GitHub Pages-ready static site (from `docs/`).

## Quickstart (local)
```bash
git clone https://github.com/irsanai/irsanai-nexus-repo
cd irsanai-nexus-repo
chmod +x scripts/setup.sh && ./scripts/setup.sh
source .venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

Then open:
- API: `http://127.0.0.1:8000/health`
- UI: `http://127.0.0.1:8000/`


## Quickstart (Windows / PowerShell)
```powershell
git clone https://github.com/irsanai/irsanai-nexus-repo
cd irsanai-nexus-repo
./scripts/setup.ps1
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --port 8000
```

> Note: `&&` and `source` are bash commands and fail in PowerShell.

## Analyze API usage
```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/psf/requests","save_report":true}'
```

List recent reports:
```bash
curl http://127.0.0.1:8000/reports
```

Fetch one report by id:
Reports are stored under `reports_output/` by default (configurable via `REPORTS_DIR`).

```bash
curl http://127.0.0.1:8000/reports/<report_id>
```

## Windows reliability notes
If you previously saw `WinError 5` during cleanup, this repo now uses:
1. A temp-based default work directory (`tempfile.gettempdir()`), and
2. Retry + chmod-based directory cleanup.

You can still override the workspace in `.env`:
```dotenv
WORK_DIR=./repo_work
```

## GitHub Pages
A workflow is included at `.github/workflows/pages.yml`. After enabling GitHub Pages (Source: GitHub Actions), pushes to `main` deploy `docs/index.html` automatically.

To point the hosted UI at your API, append `?api=https://your-api-host` to the page URL.

## Local/Remote preflight compare
Generate a deterministic JSON inventory in PyCharm/local and share it for delta analysis:
```bash
python scripts/preflight_inventory.py --output preflight.local.json
```
