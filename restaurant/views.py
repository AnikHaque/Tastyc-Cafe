from django.shortcuts import render
from menu.models import Category
from django.db.models import Count,Sum
from orders.models import OrderItem
from menu.models import Food

def home(request):

    categories = Category.objects.annotate(
        item_count=Count('foods')
    )

    # ⭐ Top Selling Foods (Correct Query)
    top_selling = (
        OrderItem.objects
        .values(
            'food__id',
            'food__name',
            'food__image',
            'food__price'
        )
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:8]
    )
    today_specials = Food.objects.filter(is_today_special=True, is_available=True)[:5]
    context = {
        "categories": categories,
        "top_selling": top_selling,
        'today_specials': today_specials,
    }

    return render(request, "home.html", context)
