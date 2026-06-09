import base64
import io
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math
from zhipuai import ZhipuAI
from .config import ZHIPU_API_KEY

_client = None


def _get_client():
    global _client
    if _client is None:
        if ZHIPU_API_KEY:
            _client = ZhipuAI(api_key=ZHIPU_API_KEY)
        else:
            key = os.environ.get('ZHIPU_API_KEY', '')
            if key:
                _client = ZhipuAI(api_key=key)
    return _client


def generate_image(prompt, style='anime'):
    client = _get_client()
    if client:
        try:
            response = client.images.generations(
                model='cogview-3-flash',
                prompt=_build_prompt(prompt, style),
            )
            if response.data and len(response.data) > 0:
                image_url = response.data[0].url
                return {'success': True, 'image': image_url, 'source': 'cogview'}
        except Exception as e:
            pass

    return _mock_generate(prompt, style)


def _build_prompt(prompt, style):
    style_map = {
        'anime': 'anime style, vibrant colors, detailed illustration',
        'realistic': 'photorealistic, high detail, professional photography',
        'watercolor': 'watercolor painting style, soft edges, artistic',
        'oil': 'oil painting style, rich textures, classical art',
        'cyberpunk': 'cyberpunk style, neon lights, futuristic, dark atmosphere',
        'chinese': 'Chinese ink painting style, traditional art, elegant',
    }
    style_suffix = style_map.get(style, style_map['anime'])
    return f'{prompt}, {style_suffix}'


def _mock_generate(prompt, style):
    width, height = 512, 512
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    palettes = {
        'anime': ['#FF6B9D', '#C44569', '#F8B500', '#6C5CE7', '#00CEC9'],
        'realistic': ['#2D3436', '#636E72', '#B2BEC3', '#DFE6E9', '#74B9FF'],
        'watercolor': ['#A8E6CF', '#DCEDC1', '#FFD3B6', '#FFAAA5', '#FF8B94'],
        'oil': ['#E17055', '#FDCB6E', '#00B894', '#0984E3', '#6C5CE7'],
        'cyberpunk': ['#0C0032', '#190061', '#240090', '#3500D3', '#282828'],
        'chinese': ['#8B4513', '#D2691E', '#F5DEB3', '#2F4F4F', '#800020'],
    }
    colors = palettes.get(style, palettes['anime'])

    for y in range(height):
        r = int(int(colors[0][1:3], 16) * (1 - y / height) + int(colors[1][1:3], 16) * (y / height))
        g = int(int(colors[0][3:5], 16) * (1 - y / height) + int(colors[1][3:5], 16) * (y / height))
        b = int(int(colors[0][5:7], 16) * (1 - y / height) + int(colors[1][5:7], 16) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    random.seed(hash(prompt) % 2**32)
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(20, 80)
        color = colors[random.randint(2, len(colors) - 1)]
        rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        alpha = random.randint(80, 200)
        shape_img = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
        shape_draw = ImageDraw.Draw(shape_img)
        shape_type = random.choice(['circle', 'rect', 'ellipse'])
        if shape_type == 'circle':
            shape_draw.ellipse([0, 0, size * 2, size * 2], fill=rgb + (alpha,))
        elif shape_type == 'rect':
            shape_draw.rectangle([0, 0, size * 2, size * 2], fill=rgb + (alpha,))
        else:
            shape_draw.ellipse([0, size // 2, size * 2, size * 3 // 2], fill=rgb + (alpha,))
        img.paste(Image.alpha_composite(Image.new('RGBA', shape_img.size, (0, 0, 0, 0)), shape_img).convert('RGB'),
                  (x - size, y - size))

    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    try:
        font = ImageFont.truetype('arial.ttf', 18)
    except:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(img)
    text = f'AI Generated: {prompt[:30]}'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rectangle([10, height - th - 20, tw + 20, height - 10], fill=(0, 0, 0, 180))
    draw.text((15, height - th - 15), text, fill=(255, 255, 255), font=font)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return {
        'success': True,
        'image': f'data:image/png;base64,{img_base64}',
        'source': 'mock',
        'mock': True
    }
