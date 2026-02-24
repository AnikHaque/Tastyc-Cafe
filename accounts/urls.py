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
     path('staff/intelligence/', views.admin_intelligence_dashboard, name='admin_intelligence'),
     path('staff/operation-pulse/', views.staff_operation_pulse, name='staff_operation_pulse'),
     path('dashboard/blogs/', views.staff_blog_list, name='staff_blog_list'),
     path('dashboard/blogs/create/', views.staff_create_blog, name='staff_create_blog'), 
     # accounts/urls.py তে যোগ করুন (উদাহরণ)
     path('blogs/edit/<int:blog_id>/', views.staff_edit_blog, name='staff_edit_blog'),
     path('blogs/delete/<int:blog_id>/', views.staff_delete_blog, name='staff_delete_blog'),
     path('dashboard/profile/', views.profile_settings, name='profile_settings'),
     path('support/', views.support_page, name='support_page'),
     ]


