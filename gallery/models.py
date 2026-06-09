from django.db import models
from django.contrib.auth.models import User


class Artwork(models.Model):
    AI_TYPES = [
        ('cv', '计算机视觉'),
        ('llm', '大语言模型'),
        ('aigc', 'AI生成内容'),
        ('workshop', '创意工坊'),
    ]
    title = models.CharField(max_length=200, verbose_name='作品标题')
    description = models.TextField(blank=True, default='', verbose_name='作品描述')
    image = models.ImageField(upload_to='artworks/', verbose_name='作品图片')
    prompt = models.TextField(blank=True, default='', verbose_name='AI提示词')
    ai_type = models.CharField(max_length=20, choices=AI_TYPES, verbose_name='AI类型')
    likes = models.PositiveIntegerField(default=0, verbose_name='点赞数')
    views = models.PositiveIntegerField(default=0, verbose_name='浏览数')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='artworks', verbose_name='创作者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '作品'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='comments', verbose_name='作品')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='评论者')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:30]}'


class LikeRecord(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='like_records', verbose_name='作品')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='like_records', verbose_name='用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        unique_together = ['artwork', 'user']
        verbose_name = '点赞记录'
        verbose_name_plural = verbose_name
