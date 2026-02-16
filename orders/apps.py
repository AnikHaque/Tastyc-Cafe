from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        import orders.signals  # পাইথন সিগন্যাল কানেক্ট করা হচ্ছে