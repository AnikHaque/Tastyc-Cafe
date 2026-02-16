from django.db import models
from django.contrib.auth.models import User
from menu.models import Food, ComboDeal
from django.db.models import Sum, Count

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('ON_THE_WAY', 'On The Way'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    
    # ডেলিভারি ম্যান ফিল্ড
    delivery_man = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deliveries',
        limit_choices_to={'groups__name': "Delivery Man"}
    )
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model): # <--- এই নামটা চেক করুন
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, null=True, blank=True)
    combo = models.ForeignKey(ComboDeal, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Item for Order #{self.order.id}"
    
class OrderQuerySet(models.QuerySet):
    def total_revenue(self):
        return self.filter(status='DELIVERED').aggregate(total=Sum('total_price'))['total'] or 0

    def delivery_man_performance(self, user):
        return self.filter(delivery_man=user, status='DELIVERED').count()

class Order(models.Model):
    # আপনার ফিল্ডগুলো...
    objects = OrderQuerySet.as_manager()