from django import views
from django.urls import path
from .views import checkout_view

urlpatterns = [
    path('checkout/', checkout_view, name='checkout'),
    path('pay/<int:order_id>/', views.payment_page, name='payment_page'),
    path('success/', views.payment_success, name='payment_success'),

]
