#!/usr/bin/env python3
"""Repository integration audit for IRSAN AI Nexus.

Computes a weighted integration score (0-100) from repository signals.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    name: str
    max_points: int
    points: int
    detail: str


ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def _exists(rel: str) -> bool:
    return (ROOT / rel).exists()


def _hash(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def architecture_checks() -> list[CheckResult]:
    main = _read('backend/main.py')
    analyze = _read('backend/api/routes_analyze.py')

    checks = [
        CheckResult(
            name='analyze_router_wired',
            max_points=10,
            points=10 if 'app.include_router(analyze_router)' in main else 0,
            detail='Analyze router registered in FastAPI app.',
        ),
        CheckResult(
            name='reports_router_wired',
            max_points=10,
            points=10 if 'app.include_router(reports_router)' in main else 0,
            detail='Reports router registered in FastAPI app.',
        ),
        CheckResult(
            name='analyze_cleanup_finally',
            max_points=10,
            points=10 if 'finally:' in analyze and 'cleanup_repo(repo_path)' in analyze else 0,
            detail='Analyze endpoint guarantees cleanup path.',
        ),
    ]
    return checks


def operations_checks() -> list[CheckResult]:
    checks = [
        CheckResult('ci_workflow', 8, 8 if _exists('.github/workflows/ci.yml') else 0, 'CI workflow present.'),
        CheckResult('pages_workflow', 7, 7 if _exists('.github/workflows/pages.yml') else 0, 'Pages workflow present.'),
        CheckResult('powershell_setup', 5, 5 if _exists('scripts/setup.ps1') else 0, 'PowerShell setup script present.'),
    ]
    return checks


def quality_checks() -> list[CheckResult]:
    checks = [
        CheckResult('tests_present', 10, 10 if _exists('tests/test_unified_analyzer_top_files.py') else 0, 'Critical analyzer tests present.'),
        CheckResult('report_store_present', 6, 6 if _exists('backend/analyzer/report_store.py') else 0, 'Report persistence module present.'),
        CheckResult('runtime_ignored', 4, 4 if 'reports_output/' in _read('.gitignore') else 0, 'Runtime report output ignored in git.'),
    ]
    return checks


def ux_checks() -> list[CheckResult]:
    readme = _read('README.md')
    readme_de = _read('README.de.md')

    docs_frontend_match = _hash('docs/index.html') == _hash('frontend/index.html')

    checks = [
        CheckResult('windows_docs_en', 6, 6 if 'Quickstart (Windows / PowerShell)' in readme else 0, 'Windows onboarding documented (EN).'),
        CheckResult('windows_docs_de', 6, 6 if 'Schnellstart (Windows / PowerShell)' in readme_de else 0, 'Windows onboarding documented (DE).'),
        CheckResult('docs_frontend_sync', 8, 8 if docs_frontend_match else 0, 'docs/index.html is in sync with frontend/index.html.'),
    ]
    return checks


def main() -> None:
    sections = {
        'architecture': architecture_checks(),
        'operations': operations_checks(),
        'quality': quality_checks(),
        'ux': ux_checks(),
    }

    total_points = sum(c.points for group in sections.values() for c in group)
    max_points = sum(c.max_points for group in sections.values() for c in group)
    score = round((total_points / max_points) * 100, 2) if max_points else 0.0

    payload = {
        'score': score,
        'total_points': total_points,
        'max_points': max_points,
        'grade': 'A' if score >= 90 else 'B' if score >= 80 else 'C' if score >= 70 else 'D',
        'sections': {
            name: [
                {
                    'name': c.name,
                    'points': c.points,
                    'max_points': c.max_points,
                    'detail': c.detail,
                }
                for c in checks
            ]
            for name, checks in sections.items()
        },
    }

    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
