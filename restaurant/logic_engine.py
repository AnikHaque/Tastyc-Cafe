# logic_engine.py
import json
import decimal
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.core.cache import cache
from django.db.models import Sum, Count

class RoyalBusinessCore:
    """
    এটি আপনার রেস্টুরেন্টের মেইন লজিক্যাল ইঞ্জিন।
    এতে সিকিউরিটি, প্রাইসিং এবং এনালাইটিক্স এর লজিক আছে।
    """

    def __init__(self, user=None):
        self.user = user
        self.log_file = "system_operations.log"

    # --- ১. ডাইনামিক অফার লজিক (Dynamic Discount Engine) ---
    def calculate_smart_discount(self, total_amount):
        """
        সময়ের ওপর ভিত্তি করে অটোমেটিক ডিসকাউন্ট ক্যালকুলেশন।
        - হ্যাপি আওয়ার (বিকেল ৪টা - সন্ধ্যা ৬টা): ২০% ছাড়।
        - বড় অর্ডার (৫০০০ টাকার ওপরে): ৫% অতিরিক্ত ছাড়।
        """
        current_hour = datetime.now().hour
        discount_pct = decimal.Decimal('0.0')

        if 16 <= current_hour <= 18:
            discount_pct += decimal.Decimal('0.20')
        
        if total_amount > 5000:
            discount_pct += decimal.Decimal('0.05')

        final_discount = decimal.Decimal(total_amount) * discount_pct
        return {
            "original_price": float(total_amount),
            "discount_amount": float(final_discount),
            "final_price": float(total_amount - final_discount),
            "applied_discount_pct": float(discount_pct * 100)
        }

    # --- ২. সিকিউরিটি এবং ফ্রড ডিটেকশন (Fraud Detection Logic) ---
    def security_check(self, ip_address, action):
        """
        একই আইপি থেকে ঘনঘন অর্ডার বা রিকোয়েস্ট আসলে তা ব্লক করার লজিক।
        """
        cache_key = f"limit_{ip_address}_{action}"
        request_count = cache.get(cache_key, 0)

        if request_count > 10: # ১ মিনিটে ১০ বারের বেশি রিকোয়েস্ট করলে
            return False, "Too many requests. Temporary Blocked."
        
        cache.set(cache_key, request_count + 1, 60)
        return True, "Success"

    # --- ৩. সেলস প্রেডিকশন (Sales Prediction Logic) ---
    def get_sales_summary(self, order_model):
        """
        আজকের অর্ডারের ডাটা এনালাইসিস করে ব্যবসার অবস্থা জানানো।
        """
        today = datetime.now().date()
        orders = order_model.objects.filter(created_at__date=today)
        total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        order_count = orders.count()

        status = "Normal"
        if total_revenue > 20000: status = "Excellent Sales! 🚀"
        elif total_revenue < 2000: status = "Slow Day. Consider an offer. 📈"

        return {
            "total_orders": order_count,
            "revenue": float(total_revenue),
            "business_status": status
        }

    # --- ৪. ডাটা ক্লিনিং (Sanitization Logic) ---
    @staticmethod
    def sanitize_string(text):
        """ইউজারের ইনপুট থেকে ক্ষতিকর ক্যারেক্টার সরানোর লজিক।"""
        if not text: return ""
        bad_chars = ["<script>", "</script>", "DROP", "DELETE", "OR 1=1"]
        for char in bad_chars:
            text = text.replace(char, "[SECURE]")
        return text.strip()

# --- লজিক শেষ ---