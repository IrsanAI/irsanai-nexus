# irsanai-nexus-repo — Repository Intelligence Platform (EN)

IRSAN AI Nexus analyzes GitHub repositories and returns a unified intelligence payload (languages, repo IQ, security indicators, and context-rich file snippets).

## Highlights
- FastAPI backend with `/health`, `/analyze`, and `/reports` endpoints.
- Top-file snippets skip binary files to keep analysis output readable.
- Safe GitHub cloning with URL validation.
- Windows-friendly cleanup handling for locked `.git/objects/pack/*` files.
- Lightweight Insight Console UI at `/` with KPI cards, report comparison, delta heatmap, and recent report browser.
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


## Quickstart (Docker)
```bash
# production-like container
docker compose -f docker/docker-compose.yml up --build -d backend

# open UI
xdg-open http://127.0.0.1:8000/

# dev profile with reload on port 8001
docker compose -f docker/docker-compose.yml --profile dev up --build backend-dev
```

Docker services persist workspace and reports via named volumes (`repo_work`, `reports`).

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

Compare two reports (delta):
```bash
curl "http://127.0.0.1:8000/reports/compare?id1=<report_id_1>&id2=<report_id_2>"
```

Fetch one report by id:
Reports are stored under `reports_output/` by default (configurable via `REPORTS_DIR`).

```bash
curl http://127.0.0.1:8000/reports/<report_id>
```

Open a human-friendly HTML report:
```bash
xdg-open http://127.0.0.1:8000/reports/<report_id>/html
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

## Integration audit
Run a weighted integration audit (architecture, operations, quality, UX):
```bash
python scripts/integration_audit.py
```


## Product roadmap & status tracking

### Status legend
- ✅ Done
- 🟡 In progress
- ⚪ Planned
- 🔁 Ongoing/iterative

### Current integration snapshot (delta view)
- **Before latest phase:** Analyze API + persisted reports + compare + HTML report + Insight Console baseline.
- **Now (current merged state):** Delta heatmap in compare workflow, report compare endpoint, Docker runtime/dev profile aligned, integration audit at **100/100 (A)**.
- **Next target:** move from JSON-centric inspection toward high-dimensional insight navigation (2.5D graph + drilldowns), while keeping additive APIs and schema stability.

### Main roadmap phases
| Phase | Goal | Status | Notes |
|---|---|---|---|
| A | Insight cockpit for non-coders | ✅ | KPI cards, report browser, compare + delta heatmap in place. |
| B | 2.5D relationship graph | 🟡 | Next implementation step; begin with node/edge projection in 2D/2.5D. |
| C | Human-in-the-loop LLM workspace | ⚪ | Prompt builder + response ingest + memory planned after graph foundations. |

### Main tasks / sub-tasks tracker
| Track | Sub-task | Status | Why it matters |
|---|---|---|---|
| Reports | Persistent report storage + listing | ✅ | Enables historical analysis and reproducibility. |
| Reports | Report compare API (`/reports/compare`) | ✅ | Enables delta reasoning instead of isolated snapshots. |
| Reports | HTML report view (`/reports/{id}/html`) | ✅ | Makes results easy to share with non-technical stakeholders. |
| UX | Insight Console with KPI cards | ✅ | Fast understanding of repo health. |
| UX | Delta heatmap visualization | ✅ | Quick visual interpretation of trend magnitude/direction. |
| UX | Timeline view of report evolution | 🟡 | Partially present via recent reports; dedicated timeline UI pending. |
| Graph | Data model for nodes/edges (files, risks, metrics) | ⚪ | Required for high-dimensional navigation. |
| Graph | 2.5D canvas rendering + zoom/pan/filter | ⚪ | Core bridge toward immersive interaction without full 3D complexity. |
| AI Loop | Prompt workbench (provider-neutral) | ⚪ | Supports external LLM augmentation workflow. |
| AI Loop | LLM response ingest + semantic diff | ⚪ | Turns one-shot outputs into iterative intelligence growth. |
| Platform | Integration audit script maintenance | 🔁 | Keeps roadmap delivery aligned with architecture integrity. |
| Platform | CI + security checks (`ruff`/`pytest`/`bandit`) | 🔁 | Prevents regressions while expanding UX complexity. |
| Platform | Docker parity (runtime + dev profile) | ✅ | Container users now get the same core UX/API/report behavior. |

### Guardrails for upcoming work
1. Keep APIs additive and non-breaking wherever possible.
2. Keep `docs/index.html` synchronized with `frontend/index.html` for Pages parity.
3. Version report schema before adding graph/prompt-memory payload sections.
4. Re-run integration audit and tests for each roadmap increment.
