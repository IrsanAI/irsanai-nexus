from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.llm_relay.model_adapters import get_adapter, list_available_models
from backend.llm_relay.payload_builder import build_payload


def _sample_analysis() -> dict:
    return {
        'analysis_version': '1.0.0',
        'repo_meta': {'url': 'https://github.com/example/repo'},
        'metrics': {'commit_count': 42, 'detected_techs': ['Python', 'TypeScript'], 'has_tests': True, 'has_ci': True},
        'languages': {'Python': {'count': 10, 'percent': 80.0}},
        'repo_iq': {'metrics_iq': {'repo_iq': 77}},
        'hidden_unicorn_probability': 0.33,
        'top_n_files': [{'path': 'README.md', 'snippet': 'x' * 1200}],
    }


def test_get_adapter_fallback_and_listing():
    assert 'openai' in list_available_models()
    assert get_adapter('unknown-model').name == get_adapter('openai').name


def test_build_payload_openai_compat_shape():
    payload = build_payload(_sample_analysis(), model='grok')
    assert payload['model'] == 'grok-2'
    assert payload['messages'][0]['role'] == 'system'
    assert payload['response_format']['type'] == 'json_object'


def test_build_payload_claude_and_gemini_shapes():
    claude = build_payload(_sample_analysis(), model='claude')
    assert 'system' in claude and 'messages' in claude

    gemini = build_payload(_sample_analysis(), model='gemini')
    assert 'contents' in gemini
    assert gemini['contents'][0]['parts'][0]['text']
