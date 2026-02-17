from django.urls import path
from . import views

urlpatterns = [
    path('book-table/', views.book_table, name='book_table'),
    # বুকিং সাকসেস হলে যে পেজে যাবে (যেখানে কিউআর কোড দেখাবে)
    path('reservation/success/<str:booking_id>/', views.reservation_success, name='reservation_success'),
]