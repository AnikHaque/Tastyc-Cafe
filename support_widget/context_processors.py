from django.utils import timezone
from .models import WidgetSetting

def smart_widget_processor(request):
    """
    এই লজিকটি অটোমেটিক চেক করবে এখন রাত না দিন, এবং সেই অনুযায়ী 
    কল বাটন দেখাবে কি না তা ডিসাইড করবে।
    """
    settings = WidgetSetting.objects.filter(is_active=True).first()
    
    if not settings:
        return {'widget_data': None}

    now = timezone.localtime(timezone.now())
    current_hour = now.hour
    
    # কন্ডিশনাল লজিক: রাতে কল বাটন হাইড করা
    show_call = True
    status_msg = "We're Online!"
    
    if settings.auto_hide_call_at_night:
        if current_hour >= settings.night_start_hour or current_hour < settings.night_end_hour:
            show_call = False
            status_msg = "Direct call is offline. Leave a message!"

    # ইউজার ডিভাইসের ওপর ভিত্তি করে লিঙ্ক তৈরি
    messenger_link = f"https://m.me/{settings.messenger_id}"
    whatsapp_link = f"https://wa.me/{settings.whatsapp_number}" if settings.whatsapp_number else None

    return {
        'widget_data': {
            'messenger_link': messenger_link,
            'whatsapp_link': whatsapp_link,
            'phone': settings.phone_number,
            'color': settings.theme_color,
            'show_call': show_call,
            'status': status_msg,
            'title': settings.title,
            'user_name': request.user.first_name if request.user.is_authenticated else "Guest"
        }
    }