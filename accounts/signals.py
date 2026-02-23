from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order, OrderItem
from menu.models import Food
from accounts.models import UserProfile

@receiver(post_save, sender=Order)
def order_automation(sender, instance, created, **kwargs):
    if created:
        # ১. অটোমেটিক ইনভেন্টরি ম্যানেজমেন্ট (অর্ডার হওয়ার সাথে সাথে স্টক কমবে)
        items = OrderItem.objects.filter(order=instance)
        for item in items:
            food = item.food
            food.stock -= item.quantity
            food.save()
            
            # ২. লো স্টক ডিটেকশন (ব্যাকগ্রাউন্ড অ্যালার্ট)
            if food.stock <= 5:
                print(f"⚠️  ALERT: {food.name} is running low! Only {food.stock} left.")

        # ৩. স্মার্ট কাস্টমার ট্যাগিং (অটো-ভিআইপি লজিক)
        if instance.total_price >= 2000:
            profile, _ = UserProfile.objects.get_or_create(user=instance.user)
            # আপনি এখানে আপনার লজিক বা ইমেইল পাঠানোর কোড রাখতে পারেন
            print(f"🚀 VIP ALERT: {instance.user.username} just made a high-value order!")

    # ৪. পেমেন্ট কনফার্মেশন অটোমেশন
    if instance.is_paid:
        print(f"💰 FINANCE: Payment confirmed for Order #{instance.id}")