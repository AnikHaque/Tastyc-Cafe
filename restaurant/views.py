from django.shortcuts import render
from menu.models import Category
from django.db.models import Count,Sum
from orders.models import OrderItem
from menu.models import Food
from menu.models import Offer
from django.utils import timezone

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
    # Active offers
    today = timezone.now().date()
    offers = Offer.objects.filter(is_active=True, start_date__lte=today, end_date__gte=today)

    context = {
        "categories": categories,
        "top_selling": top_selling,
        'today_specials': today_specials,
        'offers': offers,
    }

    return render(request, "home.html", context)
