from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns # <-- এটা লাগবেই
from . import views
from .views import home

# ১. ল্যাঙ্গুয়েজ চেঞ্জ করার জন্য ডিফল্ট পাথ (এটা i18n_patterns এর বাইরে থাকবে)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# ২. আপনার সব মেইন পাথকে i18n_patterns এর ভেতরে দিয়ে দিন
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('social-auth/', include('allauth.urls')),
    path('', home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('menu/', include('menu.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('add-review/', views.add_review, name='add_review'),
    path('blogs/', include('blog.urls')),
    path('booking/', include('tablebooking.urls')),
    path('chat/', include('chat.urls')),
    path('send-custom-mail/', views.custom_email_sender, name='custom_mail'),
    path('healthy-bites/', views.all_healthy_bites, name='all_healthy_bites'),
    path('chatbot/', include('chatbot.urls')),
    
    prefix_default_language=True # ডিফল্ট ল্যাঙ্গুয়েজেও প্রিক্লিক্স (যেমন /en/) দেখাবে
)

# 👇 MEDIA URL STATIC (Debug mode)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )