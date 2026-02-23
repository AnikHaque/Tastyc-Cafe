from django.contrib import admin
from .models import Category, Food, Offer, ComboDeal,FlashDeal
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'food_count')

    def food_count(self, obj):
        return obj.foods.count() # Category তে কয়টি খাবার আছে তা দেখাবে
    food_count.short_description = "Total Items"


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    # 'mood_tag' এবং 'is_surprise_item' লিস্টে দেখার জন্য যোগ করা হয়েছে
    list_display = ('display_image', 'name', 'category', 'mood_tag', 'price_badge', 'is_surprise_item', 'is_available')
    
    # সাইডবারে ফিল্টার করার জন্য 'mood_tag' যোগ করা হয়েছে
    list_filter = ('category', 'is_available', 'mood_tag', 'is_surprise_item')
    
    search_fields = ('name',)
    
    # লিস্ট থেকেই যেন মুড এবং সারপ্রাইজ স্ট্যাটাস চেঞ্জ করা যায়
    list_editable = ('is_available', 'mood_tag', 'is_surprise_item') 

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius:10px; object-fit:cover; box-shadow: 0 2px 5px rgba(0,0,0,0.1);" />', obj.image.url)
        return format_html('<span style="color: #ccc;">No Image</span>')
    display_image.short_description = "Preview"

    def price_badge(self, obj):
        return format_html('<b style="color: #2f3542;">৳{}</b>', obj.price)
    price_badge.short_description = "Price"
    
@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "food_name",
        "original_price_display",
        "discount_badge",
        "discounted_price_display",
        "status_badge",
        "is_active",
    )
    list_filter = ("is_active", "start_date", "end_date")
    search_fields = ("title", "food__name")
    list_editable = ("is_active",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("food")

    def food_name(self, obj):
        return obj.food.name if obj.food else "-"
    
    def original_price_display(self, obj):
        return f"৳{obj.food.price}" if obj.food else "-"
    original_price_display.short_description = "Old Price"

    def discount_badge(self, obj):
        return format_html('<span style="background: #ffa502; color: black; padding: 2px 8px; border-radius: 20px; font-weight: bold; font-size: 11px;">{}% OFF</span>', obj.discount_percentage)
    discount_badge.short_description = "Discount"

    def discounted_price_display(self, obj):
        return format_html('<b style="color: #ff4757;">৳{}</b>', obj.discounted_price)
    discounted_price_display.short_description = "Promo Price"

    def status_badge(self, obj):
        if obj.is_valid:
            bg_color = "#2ed573" # অস্থির সবুজ
            text = "Active"
        else:
            bg_color = "#ff4757" # অস্থির লাল
            text = "Expired"
        return format_html('<span style="color:white; background:{}; padding:4px 10px; border-radius:50px; font-size:11px; font-weight:bold; text-transform:uppercase;">{}</span>', bg_color, text)
    status_badge.short_description = "Status"


@admin.register(ComboDeal)
class ComboDealAdmin(admin.ModelAdmin):
    list_display = ('name', 'original_price_tag', 'promo_price_tag', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active',)

    def original_price_tag(self, obj):
        return format_html('<span style="text-decoration: line-through; color: #999;">৳{}</span>', obj.original_price)
    original_price_tag.short_description = "Regular Price"

    def promo_price_tag(self, obj):
        return format_html('<b style="color: #1e90ff;">৳{}</b>', obj.discount_price)
    promo_price_tag.short_description = "Combo Price"

@admin.register(FlashDeal)
class FlashDealAdmin(admin.ModelAdmin):
    list_display = ('title', 'end_time', 'is_active')


