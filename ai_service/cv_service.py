import cv2
import numpy as np
from collections import Counter


def analyze_image(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {'success': False, 'error': '无法解析图片'}

    height, width = img.shape[:2]
    dominant_colors = _extract_colors(img)
    brightness = _calc_brightness(img)
    edges = _detect_edges(img)
    faces = _detect_faces(img)
    scene = _classify_scene(img, brightness, edges, faces)

    return {
        'success': True,
        'data': {
            'dimensions': {'width': width, 'height': height},
            'dominant_colors': dominant_colors,
            'brightness': round(brightness, 2),
            'edge_density': round(edges, 4),
            'faces': faces,
            'scene': scene,
            'description': _generate_description(scene, dominant_colors, faces, brightness)
        }
    }


def _extract_colors(img, k=5):
    data = img.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = centers.astype(np.uint8)
    counts = Counter(labels.flatten())
    total = len(labels.flatten())
    colors = []
    for i, center in enumerate(centers):
        b, g, r = int(center[0]), int(center[1]), int(center[2])
        hex_color = f'#{r:02x}{g:02x}{b:02x}'
        percentage = round(counts.get(i, 0) / total * 100, 1)
        colors.append({'hex': hex_color, 'rgb': [r, g, b], 'percentage': percentage})
    colors.sort(key=lambda x: x['percentage'], reverse=True)
    return colors


def _calc_brightness(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    return np.mean(hsv[:, :, 2])


def _detect_edges(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return np.count_nonzero(edges) / edges.size


def _detect_faces(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    result = []
    for (x, y, w, h) in faces:
        result.append({'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)})
    return result


def _classify_scene(img, brightness, edge_density, faces):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    if len(faces) > 0:
        scene = '人像'
    elif brightness > 180:
        scene = '明亮场景'
    elif brightness < 80:
        scene = '暗光场景'
    elif edge_density > 0.15:
        scene = '复杂纹理'
    elif blur_score < 50:
        scene = '模糊/柔焦'
    else:
        scene = '一般场景'

    return {
        'type': scene,
        'sharpness': round(blur_score, 2),
        'has_faces': len(faces) > 0,
        'face_count': len(faces)
    }


def _generate_description(scene, colors, faces, brightness):
    parts = []
    parts.append(f"场景类型：{scene['type']}")
    if faces:
        parts.append(f"检测到{len(faces)}张人脸")
    top_color = colors[0] if colors else None
    if top_color:
        parts.append(f"主色调：{top_color['hex']}（占比{top_color['percentage']}%）")
    if brightness > 180:
        parts.append("画面明亮")
    elif brightness < 80:
        parts.append("画面偏暗")
    parts.append(f"清晰度：{scene['sharpness']}")
    return '，'.join(parts)
