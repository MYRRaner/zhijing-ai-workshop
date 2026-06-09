import json
import base64
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import CreativeProject


def _use_internal_ai():
    """判断是否使用内部AI调用（部署模式）"""
    return getattr(settings, 'AI_SERVICE_URL', '') == 'internal'


def _call_ai_service(endpoint, data, files=None, method='post'):
    # 部署模式：直接调用AI函数，不经过HTTP
    if _use_internal_ai():
        return _call_ai_internal(endpoint, data, files)

    # 本地开发模式：通过HTTP调用Flask服务
    url = f'{settings.AI_SERVICE_URL}{endpoint}'
    try:
        if method == 'post':
            if files:
                resp = requests.post(url, data=data, files=files, timeout=120)
            else:
                resp = requests.post(url, json=data, timeout=120)
        else:
            resp = requests.get(url, params=data, timeout=120)
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'AI服务未启动，请先启动Flask AI服务'}
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'AI服务响应超时'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _call_ai_internal(endpoint, data, files=None):
    """内部直接调用AI服务函数"""
    from .ai_bridge import call_cv_analyze, call_llm_write, call_aigc_generate

    try:
        if endpoint == '/api/cv/analyze':
            if files and 'image' in files:
                image_bytes = files['image'][1]  # (name, bytes, content_type)
                return call_cv_analyze(image_bytes)
            return {'success': False, 'error': '请上传图片'}

        elif endpoint == '/api/llm/write':
            prompt = data.get('prompt', '')
            style = data.get('style', 'general')
            history = data.get('history', None)
            if not prompt:
                return {'success': False, 'error': '请提供写作提示'}
            return call_llm_write(prompt, style, history)

        elif endpoint == '/api/aigc/generate':
            prompt = data.get('prompt', '')
            style = data.get('style', 'anime')
            if not prompt:
                return {'success': False, 'error': '请提供绘画提示'}
            return call_aigc_generate(prompt, style)

        return {'success': False, 'error': f'未知的AI端点: {endpoint}'}
    except Exception as e:
        return {'success': False, 'error': f'AI服务调用失败: {str(e)}'}


def identify_view(request):
    result = None
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        files = {'image': (image_file.name, image_file.read(), image_file.content_type)}
        result = _call_ai_service('/api/cv/analyze', {}, files=files)
        if result.get('success') and request.user.is_authenticated:
            CreativeProject.objects.create(
                title=f'识物-{image_file.name}',
                project_type='identify',
                input_data={'filename': image_file.name},
                output_data=result.get('data', {}),
                user=request.user
            )
    return render(request, 'creative/identify.html', {'result': result})


def writing_view(request):
    result = None
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        style = request.POST.get('style', 'general')
        if prompt:
            result = _call_ai_service('/api/llm/write', {
                'prompt': prompt,
                'style': style
            })
            if result.get('success') and request.user.is_authenticated:
                CreativeProject.objects.create(
                    title=f'写作-{prompt[:20]}',
                    project_type='writing',
                    input_data={'prompt': prompt, 'style': style},
                    output_data={'content': result.get('content', '')},
                    user=request.user
                )
    return render(request, 'creative/writing.html', {'result': result})


def painting_view(request):
    result = None
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        style = request.POST.get('style', 'anime')
        if prompt:
            result = _call_ai_service('/api/aigc/generate', {
                'prompt': prompt,
                'style': style
            })
            if result.get('success') and request.user.is_authenticated:
                img_data = result.get('image', '')
                CreativeProject.objects.create(
                    title=f'绘画-{prompt[:20]}',
                    project_type='painting',
                    input_data={'prompt': prompt, 'style': style},
                    output_data={'image_data': img_data[:100] if img_data else ''},
                    user=request.user
                )
    return render(request, 'creative/painting.html', {'result': result})


def workshop_view(request):
    result = None
    if request.method == 'POST':
        mode = request.POST.get('mode', 'image_to_text')
        if mode == 'image_to_text' and request.FILES.get('image'):
            image_file = request.FILES['image']
            files = {'image': (image_file.name, image_file.read(), image_file.content_type)}
            cv_result = _call_ai_service('/api/cv/analyze', {}, files=files)
            if cv_result.get('success'):
                description = cv_result.get('data', {}).get('description', '')
                prompt = request.POST.get('prompt', f'根据以下图像描述创作一段优美的文字：{description}')
                result = _call_ai_service('/api/llm/write', {'prompt': prompt, 'style': 'literary'})
                result['cv_data'] = cv_result.get('data', {})
        elif mode == 'text_to_image':
            prompt = request.POST.get('prompt', '')
            if prompt:
                llm_result = _call_ai_service('/api/llm/write', {
                    'prompt': f'将以下内容转化为适合AI绘画的英文提示词：{prompt}',
                    'style': 'prompt'
                })
                enhanced_prompt = llm_result.get('content', prompt) if llm_result.get('success') else prompt
                result = _call_ai_service('/api/aigc/generate', {
                    'prompt': enhanced_prompt,
                    'style': request.POST.get('style', 'anime')
                })
                result['enhanced_prompt'] = enhanced_prompt
        if result and result.get('success') and request.user.is_authenticated:
            CreativeProject.objects.create(
                title=f'工坊-{request.POST.get("prompt", "")[:20]}',
                project_type='workshop',
                input_data={'mode': mode, 'prompt': request.POST.get('prompt', '')},
                output_data=result,
                user=request.user
            )
    return render(request, 'creative/workshop.html', {'result': result})


@login_required
def my_projects_view(request):
    projects = CreativeProject.objects.filter(user=request.user)
    return render(request, 'creative/my_projects.html', {'projects': projects})


@login_required
def delete_project_view(request, pk):
    project = get_object_or_404(CreativeProject, pk=pk, user=request.user)
    project.delete()
    return redirect('creative:my_projects')
