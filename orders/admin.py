from decimal import Decimal
from django.utils.html import format_html
from django.contrib import admin
from .models import Coupon, OperatingHours, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['price', 'subtotal'] # অর্ডার আইটেম যেন ভুল করে এডিট না হয়

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # আপনার আগের এবং নতুন সব কলামের লিস্ট
    list_display = [
        'id', 'user', 'full_name', 'total_price', 'is_paid', 'status', 
        'customer_loyalty', 'fraud_risk', 'net_profit', 'created_at'
    ]
    
    list_filter = ['is_paid', 'status', 'created_at', 'delivery_man']
    list_editable = ['is_paid', 'status']
    search_fields = ['id', 'full_name', 'phone', 'transaction_id']
    inlines = [OrderItemInline]

    # --- ১. স্মার্ট লয়্যালটি ক্যালকুলেশন (CLV) ---
    def customer_loyalty(self, obj):
        from django.db.models import Sum, Avg
        # কাস্টমারের লাইফটাইম ডাটা এনালাইসিস
        data = Order.objects.filter(user=obj.user, is_paid=True).aggregate(
            total=Sum('total_price'), 
            avg=Avg('total_price')
        )
        total = data['total'] or 0
        avg = data['avg'] or 0
        
        # ফরম্যাটিং আগে পাইথনে করে নিচ্ছি যাতে format_html এ এরর না আসে
        total_text = f"৳{total}"
        avg_text = f"৳{avg:.2f}"
        
        return format_html('<b>{}</b><br><small style="color:gray;">Avg: {}</small>', total_text, avg_text)
    customer_loyalty.short_description = "Customer Value (CLV)"

    # --- ২. ফ্রড প্রোটেকশন লজিক (Fraud Guard) ---
    def fraud_risk(self, obj):
        from datetime import timedelta
        # ১ ঘণ্টার মধ্যে একই ফোন থেকে ৩টির বেশি অর্ডার আসলে ওয়ার্নিং
        recent_count = Order.objects.filter(
            phone=obj.phone, 
            created_at__gte=obj.created_at - timedelta(hours=1)
        ).count()
        
        if recent_count > 3:
            return format_html('<span style="color: #d32f2f; font-weight:bold;">⚠️ High Risk</span>')
        return format_html('<span style="color: #388e3c;">✅ Safe</span>')
    fraud_risk.short_description = "Fraud Guard"

    # --- ৩. রিয়েল-টাইম প্রফিট ট্র্যাকার ---
    def net_profit(self, obj):
        try:
            tax = obj.calculate_tax()
        except:
            tax = Decimal('0.00')
        
        # বিজনেস কস্ট লজিক (৪৫% ম্যাটেরিয়াল + ডেলিভারি)
        estimated_cost = (obj.total_price * Decimal('0.45')) + Decimal('50.00')
        discount = getattr(obj, 'discount_amount', Decimal('0.00'))
        
        profit = obj.total_price - tax - estimated_cost - discount
        
        profit_text = f"৳{profit:.2f}"
        color = "#2e7d32" if profit > 0 else "#c62828"
        
        return format_html('<span style="color: {}; font-weight:bold;">{}</span>', color, profit_text)
    net_profit.short_description = "Net Profit"

    # --- ৪. অটোমেশন ও সেভ লজিক ---
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Order.objects.get(pk=obj.pk)
            # একবার ডেলিভারি হয়ে গেলে স্ট্যাটাস ব্যাক করা যাবে না
            if old_obj.status == 'DELIVERED' and obj.status != 'DELIVERED':
                obj.status = 'DELIVERED'
            
            # ডেলিভারি হলে পেমেন্ট অটোমেটিক ট্রু হয়ে যাবে
            if obj.status == 'DELIVERED':
                obj.is_paid = True 
        
        super().save_model(request, obj, form, change)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'valid_to', 'active']
    list_filter = ['active', 'valid_to']
    search_fields = ['code']

@admin.register(OperatingHours)
class OperatingHoursAdmin(admin.ModelAdmin):
    list_display = ('get_day_display', 'opening_time', 'closing_time', 'is_closed')