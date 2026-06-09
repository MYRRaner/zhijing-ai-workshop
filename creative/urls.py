from django.urls import path
from . import views

app_name = 'creative'

urlpatterns = [
    path('identify/', views.identify_view, name='identify'),
    path('writing/', views.writing_view, name='writing'),
    path('painting/', views.painting_view, name='painting'),
    path('workshop/', views.workshop_view, name='workshop'),
    path('my-projects/', views.my_projects_view, name='my_projects'),
    path('delete/<int:pk>/', views.delete_project_view, name='delete_project'),
]
