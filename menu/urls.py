from django.urls import path
from .views import menu_view
from menu import views

urlpatterns = [
    path('', menu_view, name='menu'),
    path('category/<int:category_id>/', views.category_items, name='category_items'),
   path('add-combo/<int:combo_id>/', views.add_combo_to_cart, name='add_combo_to_cart'),
   path('dashboard/my-testimonials/', views.my_testimonials, name='my_testimonials'),
    path('dashboard/testimonial/delete/<int:pk>/', views.delete_testimonial, name='delete_testimonial'),
]
