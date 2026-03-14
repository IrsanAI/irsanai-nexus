from __future__ import annotations

import json

from .model_adapters import ModelAdapter, get_adapter

ROLE_PERSPECTIVES = ['CEO', 'Investor', 'Dev', 'Security', 'Marketer', 'UX', 'Lawyer', 'AI_Researcher']


def build_payload(analysis: dict, model: str = 'openai', round_num: int = 1) -> dict:
    adapter = get_adapter(model)
    payload = {
        'analysis_version': analysis.get('analysis_version', '1.0.0'),
        'repo_meta': analysis.get('repo_meta', {}),
        'metrics': analysis.get('metrics', {}),
        'languages': analysis.get('languages', {}),
        'repo_iq': analysis.get('repo_iq', {}),
        'hidden_unicorn_probability': analysis.get('hidden_unicorn_probability', 0),
        'role_perspectives': ROLE_PERSPECTIVES,
        'opportunity_map': _build_opportunity_map(analysis),
        'requested_task': _get_task_for_round(round_num),
        'attachments': {
            'top_n_files': _trim_files(analysis.get('top_n_files', []), adapter.max_input_tokens),
            'dependency_list': analysis.get('metrics', {}).get('detected_techs', []),
        },
    }
    return _wrap_for_model(payload, adapter, model)


def _build_opportunity_map(analysis: dict) -> dict:
    metrics_iq = analysis.get('repo_iq', {}).get('metrics_iq', {})
    iq = metrics_iq.get('repo_iq', 0)
    unicorn = analysis.get('hidden_unicorn_probability', 0)
    return {
        'saas_potential': 'HIGH' if iq > 70 else 'MEDIUM' if iq > 50 else 'LOW',
        'open_source_community': 'HIGH' if analysis.get('metrics', {}).get('commit_count', 0) > 100 else 'MEDIUM',
        'hidden_unicorn_probability': unicorn,
        'monetization_hints': _monetization_hints(analysis),
    }


def _monetization_hints(analysis: dict) -> list[str]:
    hints: list[str] = []
    langs = analysis.get('languages', {})
    metrics = analysis.get('metrics', {})

    if 'Python' in langs:
        hints.append('PyPI-Paket mit Premium-Tier möglich')
    if 'TypeScript' in langs or 'JavaScript' in langs:
        hints.append('SaaS-Frontend oder npm-Plugin möglich')
    if metrics.get('has_tests', False):
        hints.append('Enterprise-Support Offering (hohe Code-Qualität)')
    if metrics.get('has_ci', False):
        hints.append('Managed-Service / Hosted-Version denkbar')
    return hints or ['Weitere Analyse empfohlen']


def _get_task_for_round(round_num: int) -> str:
    if round_num == 1:
        return (
            'Analyze this repository comprehensively. '
            'For each role in role_perspectives, provide a 3-5 sentence assessment. '
            'Include top 3 risks and top 5 opportunities. Return valid JSON only.'
        )
    return (
        'Based on the Round 1 analysis provided, deepen the product strategy. '
        'Identify hidden use cases, suggest 3 SaaS product ideas with pricing tiers, '
        'and estimate 12-month market potential. Return valid JSON only.'
    )


def _trim_files(files: list[dict], max_tokens: int) -> list[dict]:
    snippet_limit = 200 if max_tokens < 50_000 else 500
    return [{**f, 'snippet': f.get('snippet', '')[:snippet_limit]} for f in files]


def _wrap_for_model(payload: dict, adapter: ModelAdapter, model: str) -> dict:
    normalized = model.strip().lower()
    content = json.dumps(payload, ensure_ascii=False, indent=2)

    if normalized == 'claude':
        return {
            'model': 'claude-opus-4-5',
            'max_tokens': 4096,
            'system': adapter.system_prompt_prefix,
            'messages': [
                {'role': 'user', 'content': f'Repository Analysis Data:\n\n{content}'},
            ],
        }

    if normalized == 'gemini':
        combined = f'{adapter.system_prompt_prefix}\n\nRepository Analysis Data:\n\n{content}'
        return {
            'contents': [
                {'parts': [{'text': combined}]},
            ]
        }

    return {
        'model': _default_model_name(normalized),
        'messages': [
            {'role': 'system', 'content': adapter.system_prompt_prefix},
            {'role': 'user', 'content': f'Repository Analysis Data:\n\n{content}'},
        ],
        'max_tokens': 4096,
        'response_format': {'type': 'json_object'},
    }


def _default_model_name(model: str) -> str:
    return {
        'openai': 'gpt-4o',
        'grok': 'grok-2',
        'mistral': 'mistral-large-latest',
        'deepseek': 'deepseek-chat',
        'qwen': 'qwen-max',
        'claude': 'claude-opus-4-5',
        'gemini': 'gemini-1.5-pro',
    }.get(model, 'gpt-4o')
