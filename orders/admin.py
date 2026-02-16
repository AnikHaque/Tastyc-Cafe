from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 'delivery_man' এবং 'full_name' যোগ করা হয়েছে যাতে লিস্টেই দেখা যায়
    list_display = ('id', 'user', 'full_name', 'total_price', 'status', 'delivery_man', 'created_at')
    
    # ড্রপডাউন দিয়ে সরাসরি লিস্ট থেকেই ডেলিভারি ম্যান অ্যাসাইন করার জন্য
    list_editable = ('status', 'delivery_man')
    
    # ফিল্টারে ডেলিভারি ম্যান যোগ করা হয়েছে
    list_filter = ('status', 'delivery_man', 'created_at')
    
    inlines = [OrderItemInline]