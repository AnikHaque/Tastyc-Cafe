from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Count, Sum, Q
from django.utils import timezone
from menu.forms import TestimonialForm
from menu.models import Category, ComboDeal, Food, Offer, Testimonial
from blog.models import Blog
from orders.models import OrderItem
from django.contrib import messages

def home(request):
    # Categories with available food count
    categories = Category.objects.annotate(
        item_count=Count('foods', filter=Q(foods__is_available=True))
    )

    # Top Selling Foods - লজিক আপডেট
    top_selling_data = (
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

    # যদি অর্ডার না থাকে, তবে সাধারণ খাবার দেখাবে
    if not top_selling_data:
        top_selling = Food.objects.filter(is_available=True)[:8]
        is_dict = False
    else:
        top_selling = top_selling_data
        is_dict = True

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

    combos = ComboDeal.objects.filter(is_active=True)
    testimonials = Testimonial.objects.all().order_by('-created_at')
    blogs = Blog.objects.filter(is_published=True).order_by('-created_at')[:6]

    context = {
        "categories": categories,
        "top_selling": top_selling,
        "is_dict": is_dict, # এটি টেমপ্লেটের জন্য জরুরি
        "today_specials": today_specials,
        "offers": offers,
        'testimonials': testimonials,
        'blogs': blogs,
        'combos': combos,
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


