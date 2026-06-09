"""
AI服务桥接层 - 直接调用AI函数，不经过HTTP
用于部署环境（如Render）中，将Flask AI服务集成到Django进程中
"""
import sys
import os

# 确保 ai_service 包可以被导入
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ai_service.cv_service import analyze_image
from ai_service.llm_service import chat_write
from ai_service.aigc_service import generate_image


def call_cv_analyze(image_bytes):
    """直接调用计算机视觉分析"""
    return analyze_image(image_bytes)


def call_llm_write(prompt, style='general', history=None):
    """直接调用LLM写作"""
    return chat_write(prompt, style, history)


def call_aigc_generate(prompt, style='anime'):
    """直接调用AI绘画"""
    return generate_image(prompt, style)
