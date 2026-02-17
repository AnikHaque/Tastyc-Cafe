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
    total_tables = models.PositiveIntegerField(default=10) # মোট টেবিল সংখ্যা
    booked_tables = models.PositiveIntegerField(default=0) # কয়টি বুক হয়েছে

    @property
    def available_tables(self):
        return self.total_tables - self.booked_tables

    def __str__(self):
        return f"{self.date} | {self.shift} ({self.available_tables} left)"

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    guest_count = models.PositiveIntegerField()
    date = models.DateField()
    shift = models.CharField(max_length=10, choices=TableCapacity.SHIFT_CHOICES)
    booking_id = models.CharField(max_length=10, unique=True, editable=False)
    status = models.CharField(max_length=20, default='Confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = str(uuid.uuid4().hex[:8].upper()) # ইউনিক আইডি
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.booking_id}"