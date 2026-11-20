from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('posts/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('add/', views.add_post, name='add_post'),
path('signup/', views.signup, name='signup'),
]
