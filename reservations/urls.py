from django.urls import path
from . import views

urlpatterns = [
    path('reserve/', views.create_reservation, name='create_reservation'),
    path('my-reservations/', views.reservation_list, name='reservation_list'),
]
