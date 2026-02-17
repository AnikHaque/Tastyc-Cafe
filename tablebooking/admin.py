from django.contrib import admin
from .models import TableCapacity, Reservation

@admin.register(TableCapacity)
class TableCapacityAdmin(admin.ModelAdmin):
    # অ্যাডমিন লিস্টে যা যা দেখা যাবে
    list_display = ('date', 'shift', 'total_tables', 'booked_tables', 'available_tables')
    # কি কি দিয়ে ফিল্টার করা যাবে
    list_filter = ('date', 'shift')
    # লিস্ট পেজেই এডিট করা যাবে
    list_editable = ('total_tables',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    # বুকিং লিস্টে যা যা দেখাবে
    list_display = ('booking_id', 'name', 'date', 'shift', 'guest_count', 'status', 'created_at')
    # কি কি দিয়ে সার্চ করা যাবে (ID বা নাম দিয়ে খোঁজা সহজ হবে)
    search_fields = ('booking_id', 'name', 'phone', 'email')
    # ডান পাশে ফিল্টার অপশন
    list_filter = ('status', 'date', 'shift')
    # বুকিং এর ভেতর গেলে ডেটা শুধু দেখা যাবে (Booking ID এডিট করা যাবে না)
    readonly_fields = ('booking_id', 'created_at')
    
    # স্ট্যাটাস কালারফুল করার জন্য (ঐচ্ছিক)
    list_editable = ('status',)