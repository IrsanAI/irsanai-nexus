from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.config import settings


def _slugify_repo_url(repo_url: str) -> str:
    trimmed = repo_url.replace('https://', '').replace('http://', '').strip('/')
    safe = trimmed.replace('/', '__')
    digest = hashlib.sha256(repo_url.encode('utf-8')).hexdigest()[:8]
    return f'{safe}__{digest}'


def persist_report(report: dict) -> Path:
    settings.reports_dir.mkdir(parents=True, exist_ok=True)

    repo_url = report.get('repo_meta', {}).get('url', 'unknown')
    slug = _slugify_repo_url(repo_url)
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    path = settings.reports_dir / f'{ts}__{slug}.json'

    payload = {
        'stored_at_utc': datetime.now(timezone.utc).isoformat(),
        'report': report,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    return path


def list_reports(limit: int = 25) -> list[dict]:
    if not settings.reports_dir.exists():
        return []

    files = sorted(settings.reports_dir.glob('*.json'), reverse=True)
    entries: list[dict] = []
    for p in files[:limit]:
        try:
            content = json.loads(p.read_text(encoding='utf-8'))
            report = content.get('report', {})
            entries.append(
                {
                    'id': p.name,
                    'stored_at_utc': content.get('stored_at_utc'),
                    'repo_url': report.get('repo_meta', {}).get('url'),
                    'analysis_timestamp': report.get('timestamp'),
                }
            )
        except Exception:
            entries.append({'id': p.name, 'note': 'unreadable report'})
    return entries


def load_report(report_id: str) -> dict:
    candidate = Path(report_id).name
    path = settings.reports_dir / candidate
    if not path.exists() or path.suffix != '.json':
        raise FileNotFoundError(f'Report not found: {report_id}')
    return json.loads(path.read_text(encoding='utf-8'))
