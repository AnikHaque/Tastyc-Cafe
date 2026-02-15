from django.shortcuts import render,redirect
from django.db.models import Count, Sum, Q
from django.utils import timezone
from menu.forms import TestimonialForm
from menu.models import Category, Food, Offer,ComboDeal, Testimonial
from blog.models import Blog
from orders.models import OrderItem
from django.contrib import messages

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
# ✅ Combo Deals
    combo_deals = ComboDeal.objects.filter(
        is_active=True,
        start_date__lte=today,
        end_date__gte=today
    ).prefetch_related('foods')[:5]

    # Calculate total price for each combo
    for combo in combo_deals:
        combo.total_price = sum([food.price for food in combo.foods.all()])

    testimonials = Testimonial.objects.all().order_by('-created_at')
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')[:6]
    context = {
        "categories": categories,
        "top_selling": top_selling,
        "today_specials": today_specials,
        "offers": offers,
        'combo_deals': combo_deals,
        'testimonials': testimonials,
        'blogs': blogs
       
    }

    return render(request, "home.html", context)

def add_review(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Dhonyobad! Apnar review-ti home-page-e show korbe.")
            return redirect('home') # Review dewar por home-e niye jabe
    else:
        form = TestimonialForm()
    
    return render(request, 'add_review.html', {'form': form})