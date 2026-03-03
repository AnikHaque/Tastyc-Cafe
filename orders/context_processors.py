from django.utils import timezone
from .models import OperatingHours

def restaurant_status(request):
    # বর্তমানে আপনার পিসি বা সার্ভারের স্থানীয় সময় নেওয়া
    now = timezone.localtime(timezone.now())
    day_index = now.weekday() # ০=সোমবার, ১=মঙ্গলবার... ৬=রবিবার
    current_time = now.time()
    
    is_open = False
    try:
        # আজকের দিনের জন্য ডাটাবেস থেকে শিডিউল আনা
        schedule = OperatingHours.objects.get(day=day_index)
        
        # চেক ১: আজকের দিন কি সাপ্তাহিক বন্ধ?
        if not schedule.is_closed:
            # চেক ২: বর্তমান সময় কি খোলার এবং বন্ধের সময়ের ভেতরে?
            if schedule.opening_time <= current_time <= schedule.closing_time:
                is_open = True
    except OperatingHours.DoesNotExist:
        # যদি ডাটাবেসে ওই দিনের ডাটা না থাকে
        is_open = False

    return {'IS_RESTAURANT_OPEN': is_open}