from django.db import models

class WidgetSetting(models.Model):
    title = models.CharField(max_length=100, default="How can we help?")
    messenger_id = models.CharField(max_length=100, help_text="আপনার ফেসবুক পেজের ইউজারনেম বা আইডি")
    phone_number = models.CharField(max_length=20, help_text="পাবলিক কন্টাক্ট নাম্বার")
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    theme_color = models.CharField(max_length=7, default="#0084FF") # Hex Color
    
    # অ্যাডভান্সড লজিকের জন্য টাইম সেটিংস
    auto_hide_call_at_night = models.BooleanField(default=True)
    night_start_hour = models.IntegerField(default=22) # রাত ১০টা
    night_end_hour = models.IntegerField(default=8)    # সকাল ৮টা

    def __str__(self):
        return "Global Widget Settings"

    class Meta:
        verbose_name_plural = "Widget Settings"