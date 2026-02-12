from django.contrib import admin
from .models import Category, Food, Offer

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('name',)

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'food', 'food_price', 'discount_percentage', 'discounted_price', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')

    def food_price(self, obj):
        return obj.food.price