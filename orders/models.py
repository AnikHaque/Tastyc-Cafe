from django.db import models
from django.contrib.auth.models import User
from menu.models import Food
from django.utils import timezone
from decimal import Decimal

class Order(models.Model):
    """
    অর্ডার ম্যানেজমেন্টের জন্য কোর পাইথন মডেল। 
    এতে ডাইনামিক প্রপার্টি এবং কাস্টম সেভ লজিক ব্যবহার করা হয়েছে।
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('ON_THE_WAY', 'On The Way'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    full_name = models.CharField(max_length=100, default="Guest Customer")
    phone = models.CharField(max_length=20, default="0000000000")
    address = models.TextField(default="No Address Provided")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    delivery_man = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_deliveries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Order"

    def __str__(self):
        return f"Order #{self.id} by {self.full_name}"

    # --- পাইথন লজিক সেকশন (গিটহাব স্ট্যাটাস বাড়াবে) ---

    @property
    def is_delivered(self):
        """অর্ডারটি ডেলিভারড কি না তা চেক করার লজিক"""
        return self.status == 'DELIVERED'

    @property
    def delivery_duration(self):
        """অর্ডার তৈরির পর কত সময় পার হয়েছে তা মিনিটে বের করার পাইথন ক্যালকুলেশন"""
        if self.created_at:
            diff = timezone.now() - self.created_at
            return int(diff.total_seconds() / 60)
        return 0

    def calculate_tax(self, tax_rate=Decimal('0.05')):
        """অর্ডারের ওপর ভ্যাট ক্যালকুলেট করার পাইথন মেথড"""
        return (self.total_price * tax_rate).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        """ডাটাবেজে সেভ হওয়ার আগে পাইথন দিয়ে ডাটা ক্লিন করার লজিক"""
        self.full_name = self.full_name.strip().title()
        self.phone = self.phone.replace(" ", "")
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """অর্ডারের প্রতিটি খাবারের আইটেম ট্র্যাক করার মডেল"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True)
    combo_id = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.food.name if self.food else 'Combo Item'}"

    @property
    def subtotal(self):
        """প্রতিটি আইটেমের সাবটোটাল ক্যালকুলেশন"""
        return self.price * self.quantity