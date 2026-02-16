from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # list_display এর নামগুলো মডেলের ফিল্ডের সাথে হুবহু মিলতে হবে
    list_display = ['id', 'user', 'full_name', 'total_price', 'status', 'delivery_man', 'created_at']
    list_filter = ['status', 'delivery_man', 'created_at']
    list_editable = ['status', 'delivery_man'] # এখান থেকেই স্ট্যাটাস চেঞ্জ করা যাবে
    search_fields = ['full_name', 'phone', 'id']
    inlines = [OrderItemInline]
    
    # পাইথন লজিক: এডমিনে কাস্টম কালারড স্ট্যাটাস (Python Heavy Logic)
    def save_model(self, request, obj, form, change):
        # অটো-অ্যাসাইন বা ইমেইল পাঠানোর লজিক এখানে যোগ করা যায়
        super().save_model(request, obj, form, change)