from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.utils import timezone

from menu.models import Category, Food, Offer
from orders.models import OrderItem


def home(request):

    # Categories with available food count
    categories = Category.objects.annotate(
        item_count=Count('foods', filter=Q(foods__is_available=True))
    )

    # Top Selling Foods
    top_selling = (
        OrderItem.objects
        .filter(food__is_available=True)
        .values(
            'food__id',
            'food__name',
            'food__image',
            'food__price'
        )
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:8]
    )

    # Today Specials
    today_specials = Food.objects.filter(
        is_today_special=True,
        is_available=True
    )[:5]

    # Active Offers
    today = timezone.now().date()

    offers = (
        Offer.objects
        .filter(
            is_active=True,
            start_date__lte=today,
            end_date__gte=today,
            food__is_available=True
        )
        .select_related('food')
    )

    context = {
        "categories": categories,
        "top_selling": top_selling,
        "today_specials": today_specials,
        "offers": offers,
    }

    return render(request, "home.html", context)
