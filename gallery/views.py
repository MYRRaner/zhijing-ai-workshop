from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Artwork, Comment, LikeRecord


def artwork_list_view(request):
    artworks = Artwork.objects.filter(is_public=True).select_related('user')
    ai_type = request.GET.get('type', '')
    if ai_type:
        artworks = artworks.filter(ai_type=ai_type)
    return render(request, 'gallery/list.html', {'artworks': artworks, 'current_type': ai_type})


def artwork_detail_view(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, is_public=True)
    artwork.views += 1
    artwork.save(update_fields=['views'])
    comments = artwork.comments.select_related('user').all()
    is_liked = False
    if request.user.is_authenticated:
        is_liked = LikeRecord.objects.filter(artwork=artwork, user=request.user).exists()
    return render(request, 'gallery/detail.html', {
        'artwork': artwork,
        'comments': comments,
        'is_liked': is_liked
    })


@login_required
@require_POST
def like_artwork_view(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    like_record, created = LikeRecord.objects.get_or_create(artwork=artwork, user=request.user)
    if not created:
        like_record.delete()
        artwork.likes -= 1
        liked = False
    else:
        artwork.likes += 1
        liked = True
    artwork.save(update_fields=['likes'])
    return JsonResponse({'liked': liked, 'likes': artwork.likes})


@login_required
@require_POST
def add_comment_view(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    content = request.POST.get('content', '').strip()
    if content:
        Comment.objects.create(artwork=artwork, user=request.user, content=content)
    return redirect('gallery:detail', pk=pk)


@login_required
def publish_artwork_view(request):
    if request.method == 'POST':
        from creative.models import CreativeProject
        project_id = request.POST.get('project_id')
        project = get_object_or_404(CreativeProject, pk=project_id, user=request.user)
        title = request.POST.get('title', project.title)
        description = request.POST.get('description', project.description)
        ai_type = project.project_type
        if ai_type == 'identify':
            ai_type = 'cv'
        elif ai_type == 'writing':
            ai_type = 'llm'
        elif ai_type == 'painting':
            ai_type = 'aigc'
        artwork = Artwork.objects.create(
            title=title,
            description=description,
            image=project.result_image,
            prompt=str(project.input_data),
            ai_type=ai_type,
            user=request.user
        )
        return redirect('gallery:detail', pk=artwork.pk)
    return redirect('creative:my_projects')
