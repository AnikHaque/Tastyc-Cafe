# accounts/utils.py
from django.db.models import Sum, Count
from datetime import datetime, timedelta

class DashboardAnalyzer:
    """পুরো পাইথন ক্লাস ব্যবহার করে কাস্টমারের ডাটা অ্যানালাইসিস করা"""
    def __init__(self, user, orders):
        self.user = user
        self.orders = orders

    def get_stats(self):
        # কমপ্লেক্স পাইথন ডিকশনারি লজিক
        return {
            'total_spent': self.orders.filter(status='DELIVERED').aggregate(Sum('total_price'))['total_price__sum'] or 0,
            'active_orders': self.orders.exclude(status='DELIVERED').count(),
            'favorite_category': self.get_favorite_food_logic(),
            'loyalty_points': self.calculate_points()
        }

    def calculate_points(self):
        # একটি পাইথন অ্যালগরিদম যা পয়েন্ট ক্যালকুলেট করে
        total = self.orders.filter(status='DELIVERED').aggregate(Sum('total_price'))['total_price__sum'] or 0
        return int(total / 100)  # প্রতি ১০০ টাকায় ১ পয়েন্ট

    def get_favorite_food_logic(self):
        # এখানে আরও ১০-১৫ লাইন পাইথন লজিক যোগ করা যায়
        return "Regular Customer"