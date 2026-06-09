from django.db import models
from django.contrib.auth.models import User


class CreativeProject(models.Model):
    PROJECT_TYPES = [
        ('identify', '智能识物'),
        ('writing', 'AI写作'),
        ('painting', 'AI绘画'),
        ('workshop', '创意工坊'),
    ]
    title = models.CharField(max_length=200, verbose_name='项目标题')
    description = models.TextField(blank=True, default='', verbose_name='项目描述')
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, verbose_name='项目类型')
    input_data = models.JSONField(default=dict, blank=True, verbose_name='输入数据')
    output_data = models.JSONField(default=dict, blank=True, verbose_name='输出数据')
    result_image = models.ImageField(upload_to='results/', blank=True, null=True, verbose_name='结果图片')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects', verbose_name='创建者')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '创意项目'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'[{self.get_project_type_display()}] {self.title}'
