from flask import Flask, request, jsonify
from flask_cors import CORS
from .cv_service import analyze_image
from .llm_service import chat_write
from .aigc_service import generate_image
from .config import AI_SERVICE_HOST, AI_SERVICE_PORT, ZHIPU_API_KEY

app = Flask(__name__)
CORS(app)

if ZHIPU_API_KEY:
    print(f'[AI Service] ZHIPU_API_KEY loaded (prefix: {ZHIPU_API_KEY[:8]}...)')
else:
    print('[AI Service] ZHIPU_API_KEY not set, AI writing/painting will use mock mode')


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'ZhiJing AI Service'})


@app.route('/api/cv/analyze', methods=['POST'])
def cv_analyze():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': '请上传图片'})
    image_file = request.files['image']
    image_bytes = image_file.read()
    result = analyze_image(image_bytes)
    return jsonify(result)


@app.route('/api/llm/write', methods=['POST'])
def llm_write():
    data = request.get_json()
    if not data or not data.get('prompt'):
        return jsonify({'success': False, 'error': '请提供写作提示'})
    prompt = data.get('prompt', '')
    style = data.get('style', 'general')
    history = data.get('history', None)
    result = chat_write(prompt, style, history)
    return jsonify(result)


@app.route('/api/aigc/generate', methods=['POST'])
def aigc_generate():
    data = request.get_json()
    if not data or not data.get('prompt'):
        return jsonify({'success': False, 'error': '请提供绘画提示'})
    prompt = data.get('prompt', '')
    style = data.get('style', 'anime')
    result = generate_image(prompt, style)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host=AI_SERVICE_HOST, port=AI_SERVICE_PORT, debug=True)
