from django.contrib import admin
from .models import Category, Food, Offer,ComboDeal
from django.utils.html import format_html

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

    list_display = (
        "title",
        "food_price",
        "discount_percentage",
        "discounted_price_display",
        "status_badge",
        "start_date",
        "end_date",
        "is_active",
    )

    list_filter = ("is_active", "start_date", "end_date")
    search_fields = ("title", "food__name")

    # ⭐ Performance Boost
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("food")

    # ⭐ Food Name Safe
    def food_name(self, obj):
        return obj.food.name if obj.food else "-"
    food_name.short_description = "Food"

    # ⭐ Food Price Safe
    def food_price(self, obj):
        return obj.food.price if obj.food else "-"
    food_price.short_description = "Original Price"

    # ⭐ Discounted Price Column
    def discounted_price_display(self, obj):
        return obj.discounted_price
    discounted_price_display.short_description = "Discounted Price"

    # ⭐ Status Badge
    def status_badge(self, obj):
        if obj.is_valid:
            color = "green"
            text = "Active"
        else:
            color = "red"
            text = "Expired"

        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:6px;">{}</span>',
            color,
            text,
        )

    status_badge.short_description = "Status"


    @admin.register(ComboDeal)

    class ComboDealAdmin(admin.ModelAdmin):
        list_display = ('title', 'discount_percentage', 'discounted_price_display', 'status_badge', 'start_date', 'end_date')
        filter_horizontal = ('foods',)

        def discounted_price_display(self, obj):
            return obj.discounted_price
        discounted_price_display.short_description = "Discounted Price"

        def status_badge(self, obj):
            if obj.is_valid:
                color = "green"
                text = "Active"
            else:
                color = "red"
                text = "Expired"
            from django.utils.html import format_html
            return format_html(
                '<span style="color:white;background:{};padding:3px 6px;border-radius:5px;">{}</span>',
                color,
                text,
            )
        status_badge.short_description = "Status"