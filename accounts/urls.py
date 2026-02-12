from django.urls import path
from . import views   # ✅ এই লাইনটাই missing ছিল
from .views import login_view, register_view, logout_view

urlpatterns =[

     path('login/', login_view, name='login'),
     path('register/', register_view, name='register'),
     path('logout/', logout_view, name='logout'),
     path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
     path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    # path('dashboard/manager/', views.manager_dashboard, name='manager_dashboard'),
     path('dashboard/staff/analytics/', views.staff_analytics, name='staff_analytics'),
     path('dashboard/staff/inventory/', views.staff_inventory, name='staff_inventory'),
     path('dashboard/staff/top-selling/', views.staff_top_selling, name='staff_top_selling'),
     path('dashboard/staff/reservations/', views.staff_reservations, name='staff_reservations'),
     path('dashboard/staff/reservations/<int:reservation_id>/<str:status>/', 
     views.update_reservation_status, name='update_reservation_status'), 
     ]


