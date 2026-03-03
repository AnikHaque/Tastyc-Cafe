from django.contrib import admin
from .models import HeroSection, RestaurantFeature

admin.site.register(HeroSection)
admin.site.register(RestaurantFeature)

# core/admin.py এ যোগ করুন
from .models import AboutSection
admin.site.register(AboutSection)


