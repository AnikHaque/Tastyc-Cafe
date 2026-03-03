from decimal import Decimal
from django.utils.html import format_html
from django.db.models import Sum, Avg
from datetime import timedelta
from django.utils import timezone

class OrderIntelligence:
    @staticmethod
    def get_fraud_score(order):
        score = 0
        # চেক ১: একই ফোন নাম্বার দিয়ে গত ১ ঘণ্টায় কয়টি অর্ডার হয়েছে?
        recent_orders = order.__class__.objects.filter(
            phone=order.phone, 
            created_at__gte=order.created_at - timedelta(hours=1)
        ).count()
        if recent_orders > 3: score += 50
        
        # চেক ২: কাস্টমার কি আগে কখনো অর্ডার ক্যানসেল করেছে?
        cancelled_count = order.__class__.objects.filter(user=order.user, status='CANCELLED').count()
        score += (cancelled_count * 20)
        
        if score > 60:
            return format_html('<span style="color: red; font-weight: bold;">⚠️ High ({}%)</span>', score)
        return format_html('<span style="color: green;">✅ Safe</span>')

    # orders/admin_logic.py ফাইলের ভেতরে আপডেট করুন

@staticmethod
def get_clv(order):
    # ডাটা আনা
    total_spent = order.__class__.objects.filter(user=order.user, is_paid=True).aggregate(Sum('total_price'))['total_price__sum'] or 0
    avg_order = order.__class__.objects.filter(user=order.user).aggregate(Avg('total_price'))['total_price__avg'] or 0
    
    # পাইথন দিয়ে আগে সংখ্যাগুলোকে স্ট্রিং ফরম্যাটে নিয়ে আসা
    spent_str = f"৳{total_spent}"
    avg_str = f"{avg_order:.2f}" # এখানে ফরম্যাটিং হবে, format_html এর বাইরে
    
    # এবার format_html এ শুধু ভেরিয়েবল পাস করা
    return format_html('<b>{}</b> <br><small style="color:gray;">Avg: ৳{}</small>', spent_str, avg_str)