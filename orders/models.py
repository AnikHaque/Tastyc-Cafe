from django.db import models
from django.contrib.auth.models import User
from menu.models import Food
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.IntegerField(help_text="ডিসকাউন্ট শতাংশ (০-১০০)")
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class OrderManager(models.Manager):
    def total_revenue(self):
        return self.filter(is_paid=True).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')

class Order(models.Model):
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
    is_paid = models.BooleanField(default=False) 
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    delivery_man = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_deliveries'
    )
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = OrderManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Order"

    def __str__(self):
        return f"Order #{self.id} - {self.full_name} ({self.status})"

    @property
    def is_delivered(self):
        return self.status == 'DELIVERED'

    @property
    def delivery_duration(self):
        if self.created_at:
            diff = timezone.now() - self.created_at
            return int(diff.total_seconds() / 60)
        return 0

    def calculate_tax(self, tax_rate=Decimal('0.05')):
        return (self.total_price * tax_rate).quantize(Decimal('0.01'))

    def save(self, *args, **kwargs):
        self.full_name = self.full_name.strip().title()
        self.phone = self.phone.replace(" ", "")
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food = models.ForeignKey(Food, on_delete=models.SET_NULL, null=True, blank=True)
    combo_id = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.food.name if self.food else 'Combo Item'}"

    @property
    def subtotal(self):
        if self.price is None or self.quantity is None:
            return 0
        return self.price * self.quantity




