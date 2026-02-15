from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_blog, name='create_blog'),
    path('', views.blog_list, name='blog_list'), # All blogs
    path('<slug:slug>/', views.blog_detail, name='blog_detail'), # Details page
    
]