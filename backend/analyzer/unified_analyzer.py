# backend/analyzer/unified_analyzer.py
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .innovation_scorer import calculate_repo_iq as calculate_repo_iq_metrics, hidden_unicorn_probability
from .language_detector import detect_languages

# falls du zusätzlich ein einfaches heuristisches IQ-Modul eingebaut hast
# (optional, siehe backend/analyzer/repo_intelligence.py)
try:
    from backend.analyzer.repo_intelligence import calculate_repo_iq as calculate_repo_iq_simple

    HAS_SIMPLE_IQ = True
except Exception:
    HAS_SIMPLE_IQ = False


def _looks_binary(sample: bytes) -> bool:
    if not sample:
        return False
    if b"\x00" in sample:
        return True

    text_bytes = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
    non_text_count = len(sample.translate(None, text_bytes))
    return (non_text_count / len(sample)) > 0.30


def _read_text_snippet(path: Path, max_chars: int = 500, max_bytes: int = 64_000) -> str | None:
    try:
        raw = path.read_bytes()[:max_bytes]
    except Exception:
        return None

    if _looks_binary(raw):
        return None

    for encoding in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
        try:
            text = raw.decode(encoding)
            return text[:max_chars]
        except UnicodeDecodeError:
            continue

    return raw.decode('utf-8', errors='replace')[:max_chars]


def count_commits(repo_path: Path) -> int:
    """Zählt Commits im geklonten Repo via git log."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_path), "log", "--oneline"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return len(r.stdout.strip().splitlines())
    except Exception:
        return 0


def get_top_files(repo_path: Path, n: int = 10) -> list[dict]:
    """
    Gibt die n größten Nicht-Binär-Dateien mit kurzem Snippet zurück.
    Nützlich für LLM-Payloads als Kontext-Anker.
    """
    files = []
    ignore = {'.git', 'node_modules', '__pycache__', '.venv'}

    sortable_paths = []
    for p in repo_path.rglob('*'):
        if not p.is_file() or any(ig in p.parts for ig in ignore):
            continue
        try:
            sortable_paths.append((p.stat().st_size, p))
        except Exception:
            continue

    for _, f in sorted(sortable_paths, key=lambda item: item[0], reverse=True):
        snippet = _read_text_snippet(f)
        if snippet is None:
            continue

        try:
            files.append(
                {
                    'path': str(f.relative_to(repo_path)),
                    'size_bytes': f.stat().st_size,
                    'snippet': snippet,
                }
            )
            if len(files) >= n:
                break
        except Exception:
            continue
    return files


def run_bandit(repo_path: Path) -> dict:
    """
    Führt bandit (Python Security Linter) aus, sofern installiert.
    Gibt aggregierte Issue-Counts zurück.
    """
    try:
        r = subprocess.run(
            ['bandit', '-r', str(repo_path), '-f', 'json', '-q'],
            capture_output=True,
            text=True,
            timeout=60,
        )
        data = json.loads(r.stdout or '{}')
        results = data.get('results', [])
        return {
            'critical_issues': sum(
                1
                for x in results
                if x.get('issue_severity') == 'HIGH' and x.get('issue_confidence') == 'HIGH'
            ),
            'high_issues': sum(1 for x in results if x.get('issue_severity') == 'HIGH'),
            'medium_issues': sum(1 for x in results if x.get('issue_severity') == 'MEDIUM'),
            'total_issues': len(results),
        }
    except Exception:
        return {'critical_issues': 0, 'high_issues': 0, 'medium_issues': 0, 'total_issues': -1, 'note': 'bandit not available'}


def analyze(repo_path: Path, repo_url: str) -> dict:
    """
    Haupt-Analyse-Funktion. Kombiniert alle Module.
    Gibt vollständiges AnalysisResult-Dict zurück.
    """
    # 1) Basis-Analysen
    languages = detect_languages(repo_path)
    security = run_bandit(repo_path)
    commit_count = count_commits(repo_path)
    top_files = get_top_files(repo_path, n=10)
    has_tests = any(repo_path.rglob('test_*.py')) or any(repo_path.rglob('*_test.py'))
    has_ci = (repo_path / '.github' / 'workflows').exists()

    metrics = {
        'language_count': len(languages),
        'detected_techs': list(languages.keys()),
        'has_tests': has_tests,
        'has_ci': has_ci,
        'commit_count': commit_count,
        'lint_score': 6.5,  # Platzhalter: optional durch pylint ersetzten
        'avg_complexity': 8,  # Platzhalter: optional durch radon ersetzen
        **security,
    }

    # 2) Repo-IQ (detaillierte, gewichtete Metrics-basiert)
    repo_iq_metrics = calculate_repo_iq_metrics(metrics, repo_path)

    # 3) Optional einfacher heuristischer IQ (falls repo_intelligence vorhanden)
    repo_iq_simple = None
    if HAS_SIMPLE_IQ:
        try:
            repo_iq_simple = calculate_repo_iq_simple(str(repo_path))
        except Exception:
            repo_iq_simple = None

    # 4) Hidden unicorn probability (aus innovation_scorer)
    unicorn_prob = hidden_unicorn_probability(metrics)

    # 5) Ergebnis zusammenstellen
    analysis_result = {
        'analysis_version': '1.0.0',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'repo_meta': {
            'url': repo_url,
            'path': str(repo_path),
            'commit_count': commit_count,
        },
        'metrics': metrics,
        'languages': languages,
        'security': security,
        'repo_iq': {
            'metrics_iq': repo_iq_metrics,
            'simple_iq': repo_iq_simple,
        },
        'hidden_unicorn_probability': unicorn_prob,
        'top_n_files': top_files,
    }

    return analysis_result
