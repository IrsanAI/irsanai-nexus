from html import escape

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from backend.analyzer.report_store import compare_reports, list_reports, load_report

router = APIRouter(prefix='/reports', tags=['reports'])


def _render_report_html(payload: dict, report_id: str) -> str:
    report = payload.get('report', {})
    metrics = report.get('metrics', {})
    repo_meta = report.get('repo_meta', {})
    languages = report.get('languages', {})

    language_rows = ''.join(
        f"<tr><td>{escape(lang)}</td><td>{details.get('count', 0)}</td><td>{details.get('percent', 0)}%</td></tr>"
        for lang, details in languages.items()
    )
    if not language_rows:
        language_rows = '<tr><td colspan="3">No language data.</td></tr>'

    return f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>IRSAN AI Nexus Report — {escape(report_id)}</title>
  <style>
    body {{ font-family: Inter, Segoe UI, sans-serif; background:#0a1020; color:#e7efff; margin:0; padding:2rem; }}
    .container {{ max-width: 1024px; margin: 0 auto; }}
    .card {{ background:#111a34; border:1px solid #263864; border-radius:14px; padding:1rem; margin-bottom:1rem; }}
    h1,h2 {{ margin:0 0 .7rem; }}
    .muted {{ color:#9eb2df; }}
    table {{ width:100%; border-collapse: collapse; }}
    th,td {{ padding:.55rem; border-bottom:1px solid #22355f; text-align:left; }}
    .grid {{ display:grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap:.8rem; }}
    pre {{ background:#0a1428; border:1px solid #24395f; border-radius:10px; padding:.8rem; overflow:auto; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>IRSAN AI Nexus — HTML Report</h1>
    <p class="muted">Report ID: {escape(report_id)}</p>

    <section class="card">
      <h2>Repository</h2>
      <div class="grid">
        <div><strong>URL:</strong> {escape(str(repo_meta.get('url', 'n/a')))}</div>
        <div><strong>Commits:</strong> {escape(str(repo_meta.get('commit_count', 'n/a')))}</div>
      </div>
    </section>

    <section class="card">
      <h2>Key Metrics</h2>
      <div class="grid">
        <div><strong>Languages:</strong> {metrics.get('language_count', 'n/a')}</div>
        <div><strong>Has Tests:</strong> {metrics.get('has_tests', 'n/a')}</div>
        <div><strong>Has CI:</strong> {metrics.get('has_ci', 'n/a')}</div>
        <div><strong>Total Security Issues:</strong> {metrics.get('total_issues', 'n/a')}</div>
      </div>
    </section>

    <section class="card">
      <h2>Language Breakdown</h2>
      <table>
        <thead><tr><th>Language</th><th>Files</th><th>Share</th></tr></thead>
        <tbody>{language_rows}</tbody>
      </table>
    </section>

    <section class="card">
      <h2>Raw Report (JSON)</h2>
      <pre>{escape(str(report))}</pre>
    </section>
  </div>
</body>
</html>
""".strip()


@router.get('')
def get_reports(limit: int = Query(default=25, ge=1, le=200)):
    items = list_reports(limit=limit)
    return {'items': items, 'count': len(items)}


@router.get('/compare')
def compare_reports_endpoint(id1: str = Query(...), id2: str = Query(...)):
    try:
        report_1 = load_report(id1)
        report_2 = load_report(id2)
        diff = compare_reports(report_1, report_2)
        return {'id1': id1, 'id2': id2, 'comparison': diff}
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get('/{report_id}')
def get_report(report_id: str):
    try:
        return load_report(report_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get('/{report_id}/html', response_class=HTMLResponse)
def get_report_html(report_id: str):
    try:
        payload = load_report(report_id)
        return _render_report_html(payload, report_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
