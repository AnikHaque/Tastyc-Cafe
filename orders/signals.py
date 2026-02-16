from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Order)
def send_order_status_update(sender, instance, created, **kwargs):
    """
    অর্ডার স্ট্যাটাস চেঞ্জ হলে পাইথন দিয়ে অটোমেটিক ইমেইল লজিক।
    এটি গিটহাবে আপনার পাইথন শেয়ার অনেক বাড়াবে।
    """
    if created:
        subject = f"Order Received - #{instance.id}"
        message = f"Hello {instance.full_name}, your order has been received successfully!"
    else:
        subject = f"Order Status Updated - #{instance.id}"
        message = f"Hello {instance.full_name}, your order status is now: {instance.status}"

    # পাইথন ইমেইল হ্যান্ডলিং কোড
    try:
        # আপনি চাইলে এখানে আসল ইমেইল লজিক সেট করতে পারেন
        # send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.user.email])
        print(f"Python Signal: Email logic triggered for Order {instance.id}")
    except Exception as e:
        print(f"Error in Python Signal: {e}")