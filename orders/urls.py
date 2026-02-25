from . import views  
from django.urls import path
from .views import checkout_view

urlpatterns = [
    
    path('checkout/', checkout_view, name='checkout'),
    path('pay/<int:order_id>/', views.payment_page, name='payment_page'),
    path('success/', views.payment_success, name='payment_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    # ড্যাশবোর্ড ইউআরএল
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    
    # স্ট্যাটাস আপডেট ইউআরএল (এই নামটাই টেমপ্লেটে ব্যবহৃত হয়েছে)
    path('delivery/update-status/<int:order_id>/<str:status>/', 
         views.update_order_status, name='update_order_status'),
    path('order/track/<int:order_id>/', views.track_order, name='track_order'),
    path('mark-paid/<int:order_id>/', views.mark_paid, name='mark_paid'),
    path('my-rewards/', views.rewards_view, name='my_rewards'),
    path('update-status/<int:order_id>/<str:new_status>/', views.update_delivery_status, name='update_delivery_status'),
    path('surprise-box/', views.surprise_box_view, name='surprise_box'),
    path('reorder/<int:order_id>/', views.reorder_instant, name='reorder_instant'),
    path('dashboard/payments/', views.my_payments, name='my_payments'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
]
