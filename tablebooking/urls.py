from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_table, name='book_table'),
    path('success/<str:booking_id>/', views.reservation_success, name='reservation_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'), # নতুন হিস্ট্রি পেজ
    path('check-availability/', views.check_availability, name='check_availability'),
]