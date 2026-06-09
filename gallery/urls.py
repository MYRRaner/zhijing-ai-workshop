from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('', views.artwork_list_view, name='list'),
    path('<int:pk>/', views.artwork_detail_view, name='detail'),
    path('<int:pk>/like/', views.like_artwork_view, name='like'),
    path('<int:pk>/comment/', views.add_comment_view, name='comment'),
    path('publish/', views.publish_artwork_view, name='publish'),
]
