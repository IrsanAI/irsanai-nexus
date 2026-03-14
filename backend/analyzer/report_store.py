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


def compare_reports(report_a: dict, report_b: dict) -> dict:
    a = report_a.get('report', {})
    b = report_b.get('report', {})

    metrics_a = a.get('metrics', {})
    metrics_b = b.get('metrics', {})

    numeric_metric_keys = [
        'commit_count',
        'language_count',
        'total_issues',
        'high_issues',
        'medium_issues',
        'critical_issues',
    ]

    metric_deltas = {}
    for key in numeric_metric_keys:
        va = metrics_a.get(key)
        vb = metrics_b.get(key)
        if isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            metric_deltas[key] = {'from': va, 'to': vb, 'delta': vb - va}

    iq_a = (((a.get('repo_iq') or {}).get('metrics_iq') or {}).get('repo_iq') or 0)
    iq_b = (((b.get('repo_iq') or {}).get('metrics_iq') or {}).get('repo_iq') or 0)

    langs_a = a.get('languages', {})
    langs_b = b.get('languages', {})
    language_delta = {}
    for lang in sorted(set(langs_a.keys()) | set(langs_b.keys())):
        cnt_a = (langs_a.get(lang) or {}).get('count', 0)
        cnt_b = (langs_b.get(lang) or {}).get('count', 0)
        language_delta[lang] = {'from': cnt_a, 'to': cnt_b, 'delta': cnt_b - cnt_a}

    return {
        'from_report_timestamp': a.get('timestamp'),
        'to_report_timestamp': b.get('timestamp'),
        'from_repo': (a.get('repo_meta') or {}).get('url'),
        'to_repo': (b.get('repo_meta') or {}).get('url'),
        'repo_iq_delta': {'from': iq_a, 'to': iq_b, 'delta': iq_b - iq_a},
        'metric_deltas': metric_deltas,
        'language_deltas': language_delta,
    }
