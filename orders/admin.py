from django.contrib import admin
from .models import Coupon, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price', 'subtotal'] # অর্ডার আইটেম যেন ভুল করে এডিট না হয়

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # list_display-তে 'is_paid' এবং 'delivery_man' যোগ করা হয়েছে
    list_display = ['id', 'user', 'full_name', 'total_price', 'is_paid', 'status', 'created_at']
    
    # ফিল্টার করার সুবিধা বাড়ানো হয়েছে
    list_filter = ['is_paid', 'status', 'created_at', 'delivery_man']
    
    # অ্যাডমিন প্যানেল থেকে সরাসরি পেইড বা স্ট্যাটাস চেঞ্জ করার জন্য list_editable
    list_editable = ['is_paid', 'status']
    
    inlines = [OrderItemInline]
    
    # কুইক সার্চ করার অপশন (নাম বা আইডি দিয়ে)
    search_fields = ['id', 'full_name', 'phone']

    # পাইথন লজিক: অ্যাডমিন প্যানেল থেকে সেভ করার সময় ডাটা ক্লিন করা
    def save_model(self, request, obj, form, change):
        if change: # যদি অর্ডার আগে থেকেই থাকে এবং এখন এডিট করা হয়
            old_obj = Order.objects.get(pk=obj.pk)
            
            # লজিক ১: যদি একবার ডেলিভারি হয়ে যায়, তবে স্ট্যাটাস আর পেন্ডিং এ নেওয়া যাবে না
            if old_obj.status == 'DELIVERED' and obj.status != 'DELIVERED':
                obj.status = 'DELIVERED'
            
            # লজিক ২: পেমেন্ট ট্র্যাকিং (আপনি চাইলে এখানেও কাস্টম লজিক দিতে পারেন)
            # যেমন: যদি স্ট্যাটাস DELIVERED হয়, অটোমেটিক is_paid = True হয়ে যাবে
            if obj.status == 'DELIVERED':
                obj.status = 'DELIVERED'
                obj.is_paid = True 

        super().save_model(request, obj, form, change)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'valid_to', 'active']
    list_filter = ['active', 'valid_to']
    search_fields = ['code']