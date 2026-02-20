from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, IntegerField
from django.contrib.auth.decorators import login_required
from .models import Category, ComboDeal, FlashDeal, Food, Testimonial
from .utils import get_ai_recommendations 

def menu_view(request):
    # ১. ব্যাকএন্ড স্টক গার্ড: স্টক ০ হলে অটোমেটিক হাইড করে দেবে (Zero HTML effort)
    Food.objects.filter(stock__lte=0, is_available=True).update(
        is_available=False, 
        is_today_special=False
    )

    # ২. ফিল্টারিং শুরু
    food_list = Food.objects.filter(is_available=True)
    
    search_query = request.GET.get('search')
    if search_query:
        food_list = food_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    category_slug = request.GET.get('category')
    if category_slug:
        food_list = food_list.filter(category__name__iexact=category_slug.replace('-', ' '))

    # ৩. ইন্টেলিজেন্ট সর্টিং (অটো-পাইলট র‍্যাঙ্কিং)
    food_list = food_list.annotate(
        priority=Case(
            When(is_today_special=True, then=1),    # স্পেশাল আইটেম সবার আগে
            When(stock__lte=10, then=2),            # সেলিং ফাস্ট আইটেম এরপর
            default=3,                              # বাকিগুলো মাঝে
            output_field=IntegerField(),
        )
    ).order_by('priority', '-created_at')

    # ৪. প্যাজিনেশন
    paginator = Paginator(food_list, 8) 
    foods = paginator.get_page(request.GET.get('page'))

    return render(request, 'menu.html', {
        'categories': Category.objects.all(),
        'foods': foods, 
    })

def food_detail(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    
    # ব্যাকএন্ড স্টক ভ্যালিডেশন
    if food.stock <= 0 and food.is_available:
        food.is_available = False
        food.save()

    recommendations = get_ai_recommendations(food)
    meta = food.get_meta_tags() # models.py এর সেই স্মার্ট মেথড
    
    return render(request, 'menu/food_detail.html', {
        'food': food,
        'recommendations': recommendations,
        'meta_title': meta['title'],
        'meta_description': meta['description'],
        'meta_image': meta['image'],
    })

def mood_menu_view(request):
    selected_mood = request.GET.get('mood', 'happy')
    food_items = Food.objects.filter(mood_tag=selected_mood, is_available=True)
    return render(request, 'menu/mood_menu.html', {
        'foods': food_items,
        'current_mood': selected_mood
    })

def add_combo_to_cart(request, combo_id):
    combo = get_object_or_404(ComboDeal, id=combo_id)
    cart = request.session.get('cart', {})
    item_id = f"combo_{combo.id}"

    if item_id in cart:
        cart[item_id]['qty'] = int(cart[item_id]['qty']) + 1
    else:
        cart[item_id] = {
            'product_id': int(combo.id),
            'name': str(combo.name),
            'price': float(combo.discount_price), 
            'qty': 1,
            'image': combo.image.url if combo.image else '',
            'is_combo': True
        }

    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"{combo.name} কার্টে যোগ করা হয়েছে!")
    return redirect('cart') 

def add_deal_to_cart(request, deal_id):
    flash_deal = get_object_or_404(FlashDeal, id=deal_id)
    cart = request.session.get('cart', {})
    deal_key = f"deal_{flash_deal.id}"
    
    if deal_key in cart:
        cart[deal_key]['qty'] += 1
    else:
        cart[deal_key] = {
            'product_id': flash_deal.id,
            'name': flash_deal.title,
            'price': 999.0, 
            'qty': 1,
            'image': flash_deal.image.url if flash_deal.image else '',
            'is_deal': True
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"{flash_deal.title} added to your bag!")
    return redirect('home') 

def toggle_wishlist(request, food_id):
    wishlist = request.session.get('wishlist', [])
    food_id_str = str(food_id)
    if food_id_str in wishlist:
        wishlist.remove(food_id_str) 
    else:
        wishlist.append(food_id_str) 
    
    request.session['wishlist'] = wishlist
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', 'menu'))

def wishlist_page(request):
    wishlist_ids = request.session.get('wishlist', [])
    wishlist_items = Food.objects.filter(id__in=wishlist_ids)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def my_testimonials(request):
    user_testimonials = Testimonial.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/my_testimonials.html', {'my_testimonials': user_testimonials})

@login_required
def delete_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, id=pk, user=request.user)
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, "Testimonial successfully deleted.")
        return redirect('my_testimonials')
    return render(request, 'dashboard/confirm_delete.html', {'testimonial': testimonial})

def ai_dish_scanner(request):
    if request.method == 'POST' and request.FILES.get('food_image'):
        identified_name = "Pizza" # এখানে আপনার AI মডেল বসবে
        food_item = Food.objects.filter(name__icontains=identified_name).first()
        return render(request, 'menu/scanner_result.html', {'food': food_item, 'name': identified_name})
    return render(request, 'menu/scanner.html')

def category_items(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    foods = category.foods.filter(is_available=True)
    return render(request, "category_items.html", {"category": category, "foods": foods})