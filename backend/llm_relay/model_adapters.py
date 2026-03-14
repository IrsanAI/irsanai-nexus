from dataclasses import dataclass


@dataclass
class ModelAdapter:
    name: str
    api_url: str
    curl_example: str
    system_prompt_prefix: str
    max_input_tokens: int
    chunking_note: str


ADAPTERS: dict[str, ModelAdapter] = {
    'openai': ModelAdapter(
        name='ChatGPT (OpenAI)',
        api_url='https://api.openai.com/v1/chat/completions',
        curl_example='curl https://api.openai.com/v1/chat/completions -H "Authorization: Bearer $OPENAI_API_KEY" -H "Content-Type: application/json" -d @payload_openai.json',
        system_prompt_prefix='You are an expert software architect and product analyst. Analyze the provided repository data and return structured JSON.',
        max_input_tokens=128_000,
        chunking_note='Bei >100k Tokens: Teile top_n_files in 2 Payloads. Sende role_perspectives in Runde 2.',
    ),
    'claude': ModelAdapter(
        name='Claude (Anthropic)',
        api_url='https://api.anthropic.com/v1/messages',
        curl_example='curl https://api.anthropic.com/v1/messages -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01" -H "Content-Type: application/json" -d @payload_claude.json',
        system_prompt_prefix='You are a senior product strategist and code reviewer. Return structured JSON with summary, risks, opportunities and recommendations.',
        max_input_tokens=200_000,
        chunking_note='Claude hat hohes Kontextfenster; bei sehr großen Repos top_n_files reduzieren.',
    ),
    'gemini': ModelAdapter(
        name='Gemini (Google)',
        api_url='https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent',
        curl_example='curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=$GEMINI_API_KEY" -H "Content-Type: application/json" -d @payload_gemini.json',
        system_prompt_prefix='You are a technical product analyst. Return valid JSON only: executive_summary, technical_assessment, market_potential, risks, opportunities.',
        max_input_tokens=32_000,
        chunking_note='Gemini: kompakten Payload nutzen, Snippets kürzen.',
    ),
    'grok': ModelAdapter(
        name='Grok (xAI)',
        api_url='https://api.x.ai/v1/chat/completions',
        curl_example='curl https://api.x.ai/v1/chat/completions -H "Authorization: Bearer $GROK_API_KEY" -H "Content-Type: application/json" -d @payload_grok.json',
        system_prompt_prefix='Analyze repository data with focus on disruptive potential. Return structured JSON.',
        max_input_tokens=131_072,
        chunking_note='Grok: meist ohne Chunking nutzbar, bei sehr großen Repos reduzieren.',
    ),
    'mistral': ModelAdapter(
        name='Mistral',
        api_url='https://api.mistral.ai/v1/chat/completions',
        curl_example='curl https://api.mistral.ai/v1/chat/completions -H "Authorization: Bearer $MISTRAL_API_KEY" -H "Content-Type: application/json" -d @payload_mistral.json',
        system_prompt_prefix='You are a code quality expert. Return JSON with architecture notes, quality score and improvement areas.',
        max_input_tokens=32_000,
        chunking_note='Mistral: Fokus auf metrics + security, wenige Snippets.',
    ),
    'deepseek': ModelAdapter(
        name='DeepSeek',
        api_url='https://api.deepseek.com/v1/chat/completions',
        curl_example='curl https://api.deepseek.com/v1/chat/completions -H "Authorization: Bearer $DEEPSEEK_API_KEY" -H "Content-Type: application/json" -d @payload_deepseek.json',
        system_prompt_prefix='Analyze for technical depth and research potential. Return structured JSON only.',
        max_input_tokens=64_000,
        chunking_note='DeepSeek: metrics + dependency list + top files funktionieren gut.',
    ),
    'qwen': ModelAdapter(
        name='Qwen (Alibaba)',
        api_url='https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
        curl_example='curl https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation -H "Authorization: Bearer $QWEN_API_KEY" -H "Content-Type: application/json" -d @payload_qwen.json',
        system_prompt_prefix='Evaluate commercial potential and technical maturity. Return JSON with score, market_fit and recommendations.',
        max_input_tokens=32_000,
        chunking_note='Qwen: kompakter Payload empfohlen (metrics + top_3_files).',
    ),
}


def get_adapter(model: str) -> ModelAdapter:
    normalized = (model or '').strip().lower()
    return ADAPTERS.get(normalized, ADAPTERS['openai'])


def list_available_models() -> list[str]:
    return sorted(ADAPTERS.keys())
