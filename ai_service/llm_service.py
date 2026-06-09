from zhipuai import ZhipuAI
from .config import ZHIPU_API_KEY

STYLE_PROMPTS = {
    'general': '',
    'literary': '请用优美、富有文学色彩的语言来写作，注意修辞和意境。',
    'technical': '请用专业、严谨的技术语言来写作，注重逻辑和准确性。',
    'humorous': '请用幽默风趣的语言来写作，适当加入有趣的比喻和段子。',
    'poetry': '请用诗歌的形式来创作，注意韵律和意境。',
    'prompt': '请将内容转化为适合AI绘画的英文提示词（prompt），包含主体、风格、光影、细节等要素，用英文逗号分隔。',
}

_client = None


def _get_client():
    global _client
    if _client is None:
        if ZHIPU_API_KEY:
            try:
                _client = ZhipuAI(api_key=ZHIPU_API_KEY)
            except Exception as e:
                print(f'[LLM] Client init failed: {e}')
        else:
            import os
            key = os.environ.get('ZHIPU_API_KEY', '')
            if key:
                _client = ZhipuAI(api_key=key)
    return _client


def chat_write(prompt, style='general', history=None):
    client = _get_client()
    if not client:
        return _mock_write(prompt, style)

    style_instruction = STYLE_PROMPTS.get(style, '')
    system_msg = '你是一个创意写作助手，擅长各种风格的写作。' + style_instruction
    messages = [{'role': 'system', 'content': system_msg}]
    if history:
        messages.extend(history)
    messages.append({'role': 'user', 'content': prompt})

    try:
        response = client.chat.completions.create(
            model='glm-4-flash',
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        content = response.choices[0].message.content
        return {'success': True, 'content': content}
    except Exception as e:
        return {'success': False, 'error': str(e), 'content': _mock_write(prompt, style)['content']}


def _mock_write(prompt, style):
    mock_responses = {
        'general': f'【AI写作演示】根据您的提示「{prompt}」，这里是一段由AI生成的创意内容。在实际使用中，请配置智谱AI的API密钥以获得真实的AI写作体验。智境AI创意工坊支持多种写作风格，包括文学、技术、幽默、诗歌等，让创作变得更加轻松有趣。',
        'literary': f'【文学风格演示】月光如水，倾泻在文字的河流上。「{prompt}」——这一缕思绪，在AI的笔尖化作诗意的涟漪，荡漾在创意的湖面。配置API密钥后，即可体验真正的AI文学创作。',
        'technical': f'【技术风格演示】关于「{prompt}」的技术分析：本系统基于大语言模型（LLM）架构，通过自然语言处理技术实现智能写作。配置API密钥后可体验完整功能。',
        'humorous': f'【幽默风格演示】说到「{prompt}」，这让我想起一个笑话——AI说它要写一篇关于这个主题的文章，结果它写了...好吧，配置API密钥后你就知道了！😄',
        'poetry': f'【诗歌风格演示】\n思绪如风起，\n「{prompt}」入诗行。\nAI笔生花，\n创意自芬芳。\n\n配置API密钥，\n方得真文章。',
        'prompt': f'a beautiful scene of {prompt}, highly detailed, professional photography, soft lighting, 8k, masterpiece',
    }
    content = mock_responses.get(style, mock_responses['general'])
    return {'success': True, 'content': content, 'mock': True}
