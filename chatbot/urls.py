from django.urls import path
from . import views

urlpatterns = [
    path('ask/', views.get_ai_response, name='ask_ai'),
]