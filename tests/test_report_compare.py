from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.analyzer.report_store import compare_reports


def test_compare_reports_has_metric_and_language_deltas():
    report_a = {
        'report': {
            'timestamp': '2026-01-01T00:00:00Z',
            'repo_meta': {'url': 'https://github.com/a/repo'},
            'metrics': {'commit_count': 10, 'language_count': 2, 'total_issues': 3},
            'languages': {'Python': {'count': 5}, 'YAML': {'count': 1}},
            'repo_iq': {'metrics_iq': {'repo_iq': 50}},
        }
    }
    report_b = {
        'report': {
            'timestamp': '2026-01-02T00:00:00Z',
            'repo_meta': {'url': 'https://github.com/a/repo'},
            'metrics': {'commit_count': 15, 'language_count': 3, 'total_issues': 1},
            'languages': {'Python': {'count': 7}, 'TypeScript': {'count': 2}},
            'repo_iq': {'metrics_iq': {'repo_iq': 70}},
        }
    }

    delta = compare_reports(report_a, report_b)

    assert delta['metric_deltas']['commit_count']['delta'] == 5
    assert delta['metric_deltas']['total_issues']['delta'] == -2
    assert delta['repo_iq_delta']['delta'] == 20
    assert delta['language_deltas']['Python']['delta'] == 2
    assert delta['language_deltas']['YAML']['delta'] == -1
    assert delta['language_deltas']['TypeScript']['delta'] == 2
