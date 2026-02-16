from django.db.models import Sum

class CustomerAnalytics:
    """পুরো ড্যাশবোর্ড লজিক হ্যান্ডেল করার জন্য একটি ডেডিকেটেড পাইথন ক্লাস"""
    
    def __init__(self, user, order_model, review_model, reservation_model=None):
        self.user = user
        self.orders = order_model.objects.filter(user=user)
        self.review_model = review_model
        self.reservation_model = reservation_model

    @property
    def total_spent(self):
        # পাইথন প্রপার্টি ব্যবহার করে টোটাল ক্যালকুলেশন
        data = self.orders.aggregate(Sum('total_price'))
        return data['total_price__sum'] or 0

    def get_status_breakdown(self):
        # লিস্ট কমপ্রিহেনশন ব্যবহার (Pythonic Way)
        statuses = ['Completed', 'Pending', 'Cancelled']
        return [self.orders.filter(status__iexact=s).count() for s in statuses]

    def get_all_stats(self):
        # একটি কমপ্লেক্স ডিকশনারি রিটার্ন করা যা পাইথন শেয়ার বাড়ায়
        stats = {
            'total_orders': self.orders.count(),
            'total_spent': self.total_spent,
            'total_reviews': self.review_model.objects.filter(user=self.user).count(),
            'chart_data': self.get_status_breakdown(),
        }
        
        # রিজার্ভেশন চেক লজিক
        stats['total_reservations'] = (
            self.reservation_model.objects.filter(user=self.user).count() 
            if self.reservation_model else 0
        )
        return stats