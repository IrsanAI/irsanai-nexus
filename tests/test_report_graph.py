from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.analyzer import report_store


def test_build_insight_graph_contains_repo_metric_language_and_risk_nodes():
    report = {
        'repo_meta': {'url': 'https://github.com/example/repo'},
        'metrics': {'commit_count': 12, 'language_count': 2, 'total_issues': 3},
        'languages': {
            'Python': {'count': 10, 'percent': 80.0},
            'YAML': {'count': 2, 'percent': 20.0},
        },
    }

    graph = report_store.build_insight_graph(report)

    node_ids = {node['id'] for node in graph['nodes']}
    assert 'repo' in node_ids
    assert 'metric:commit_count' in node_ids
    assert 'lang:Python' in node_ids
    assert 'risk:security' in node_ids
    assert len(graph['edges']) > 0


def test_persist_and_load_report_include_schema_and_graph(tmp_path, monkeypatch):
    monkeypatch.setattr(report_store.settings, 'reports_dir', tmp_path)

    report = {
        'repo_meta': {'url': 'https://github.com/example/repo'},
        'metrics': {'commit_count': 4, 'language_count': 1, 'total_issues': 0},
        'languages': {'Python': {'count': 4, 'percent': 100.0}},
    }

    saved = report_store.persist_report(report)
    loaded = report_store.load_report(saved.name)

    assert loaded['report_schema_version'] == report_store.REPORT_SCHEMA_VERSION
    assert 'insight_graph' in loaded
    assert loaded['insight_graph']['nodes']


def test_compare_reports_includes_graph_delta():
    report_a = {
        'report': {'repo_meta': {'url': 'https://github.com/a/repo'}, 'metrics': {}, 'languages': {}, 'repo_iq': {}},
        'insight_graph': {'nodes': [{'id': 'a'}], 'edges': []},
    }
    report_b = {
        'report': {'repo_meta': {'url': 'https://github.com/a/repo'}, 'metrics': {}, 'languages': {}, 'repo_iq': {}},
        'insight_graph': {'nodes': [{'id': 'a'}, {'id': 'b'}], 'edges': [{'from': 'a', 'to': 'b'}]},
    }

    delta = report_store.compare_reports(report_a, report_b)

    assert delta['graph_delta']['nodes']['delta'] == 1
    assert delta['graph_delta']['edges']['delta'] == 1


def test_list_reports_includes_timeline_summary_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(report_store.settings, 'reports_dir', tmp_path)

    report = {
        'repo_meta': {'url': 'https://github.com/example/repo'},
        'metrics': {'commit_count': 9, 'language_count': 2, 'total_issues': 1},
        'repo_iq': {'metrics_iq': {'repo_iq': 73}},
        'languages': {'Python': {'count': 9, 'percent': 100.0}},
    }

    report_store.persist_report(report)
    items = report_store.list_reports(limit=5)

    assert items
    first = items[0]
    assert first['repo_iq'] == 73
    assert first['commit_count'] == 9
    assert first['total_issues'] == 1
    assert first['language_count'] == 2
