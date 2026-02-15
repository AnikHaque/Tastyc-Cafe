from . import views
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', views.about_view, name='about'),
    path('menu/', include('menu.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('reservations/', include('reservations.urls')),
    path('add-review/', views.add_review, name='add_review'),
    path('blogs/', include('blog.urls')),
]

# 👇 THIS MUST BE AT THE BOTTOM
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
