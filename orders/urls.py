from . import views  
from django.urls import path
from .views import checkout_view

urlpatterns = [
    
    path('checkout/', checkout_view, name='checkout'),
    path('pay/<int:order_id>/', views.payment_page, name='payment_page'),
    path('success/', views.payment_success, name='payment_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('mark-paid/<int:order_id>/', views.mark_paid, name='mark_paid'), 

]
