# tablebooking/models.py
from django.db import models
from django.contrib.auth.models import User
import uuid

class TableCapacity(models.Model):
    SHIFT_CHOICES = (
        ('Lunch', 'Lunch (12:00 PM - 04:00 PM)'),
        ('Dinner', 'Dinner (07:00 PM - 11:00 PM)'),
    )
    date = models.DateField()
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    total_tables = models.PositiveIntegerField(default=15) # আপনার রেস্টুরেন্টের মোট টেবিল
    booked_tables = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('date', 'shift')
        verbose_name_plural = "Table Capacities"

    @property
    def available_tables(self):
        return max(0, self.total_tables - self.booked_tables)

    def __str__(self):
        return f"{self.date} | {self.shift} - Available: {self.available_tables}"

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='table_bookings')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    guest_count = models.PositiveIntegerField()
    date = models.DateField()
    shift = models.CharField(max_length=10)
    booking_id = models.CharField(max_length=10, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    special_request = models.TextField(blank=True, null=True) # ইউজারের এক্সট্রা রিকোয়েস্ট
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = str(uuid.uuid4().hex[:8].upper())
        super().save(*args, **kwargs)