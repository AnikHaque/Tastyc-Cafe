from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from .models import Category, ComboDeal, FlashDeal, Food, Testimonial
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .utils import get_ai_recommendations # এই লাইনটি খেয়াল করবেন

def menu_view(request):
    # ১. বেস কোয়েরি সেট (সব এভেইলএবল খাবার)
    food_list = Food.objects.filter(is_available=True).order_by('-id')
    categories = Category.objects.all()

    # ২. সার্চ লজিক (নাম অথবা ডেসক্রিপশন দিয়ে সার্চ)
    search_query = request.GET.get('search')
    if search_query:
        food_list = food_list.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # ৩. ক্যাটাগরি ফিল্টার লজিক (URL স্লাগ অনুযায়ী)
    category_slug = request.GET.get('category')
    if category_slug:
        # স্লাগ থেকে স্পেস রিমুভ করে ক্যাটাগরি ফিল্টার
        food_list = food_list.filter(category__name__iexact=category_slug.replace('-', ' '))

    # ৪. প্যাগিনেশন লজিক (প্রতি পেজে ৮টি খাবার দেখাবে)
    paginator = Paginator(food_list, 8) 
    page_number = request.GET.get('page')
    foods = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'foods': foods, # টেমপ্লেট এখন এই 'foods' লুপ করবে
    }
    return render(request, 'menu.html', context)


def category_items(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    foods = category.foods.filter(is_available=True)

    context = {
        "category": category,
        "foods": foods
    }
    return render(request, "category_items.html", context)


def add_combo_to_cart(request, combo_id):
    combo = get_object_or_404(ComboDeal, id=combo_id)
    cart = request.session.get('cart', {})
    
    item_id = f"combo_{combo.id}"

    if item_id in cart:
        # নিশ্চিত করছি পুরনো ডাটা থাকলেও যেন নাম্বার হিসেবে যোগ হয়
        current_qty = int(cart[item_id]['qty'])
        cart[item_id]['qty'] = current_qty + 1
    else:
        # নতুন আইটেম অ্যাড
        cart[item_id] = {
            'product_id': int(combo.id),
            'name': str(combo.name),
            'price': float(combo.discount_price), # ক্যালকুলেশনের জন্য ফ্লোট
            'qty': 1,
            'image': combo.image.url if combo.image else '',
            'is_combo': True
        }

    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"{combo.name} কার্টে যোগ করা হয়েছে!")
    
    return redirect('cart') # আপনার কার্ট ইউআরএল এর নাম নিশ্চিত করুন

from django.contrib.auth.decorators import login_required

@login_required
def my_testimonials(request):
    # শুধুমাত্র লগইন করা ইউজারের টেস্টোমনিয়ালগুলো ফিল্টার করবে
    # আপনার মডেলের ফিল্ডের নাম 'user' না হয়ে অন্য কিছু হলে সেটি এখানে দিন
    user_testimonials = Testimonial.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'my_testimonials': user_testimonials
    }
    return render(request, 'dashboard/my_testimonials.html', context)

@login_required
def delete_testimonial(request, pk):
    testimonial = get_object_or_404(Testimonial, id=pk, user=request.user)
    if request.method == 'POST':
        testimonial.delete()
        messages.success(request, "Testimonial-ti successfully delete kora hoyeche.")
        return redirect('my_testimonials')
    return render(request, 'dashboard/confirm_delete.html', {'testimonial': testimonial})


def add_deal_to_cart(request, deal_id):
    flash_deal = get_object_or_404(FlashDeal, id=deal_id)
    cart = request.session.get('cart', {})
    
    # ডিলের জন্য একটি ইউনিক আইডি তৈরি করি (যাতে সাধারণ খাবারের সাথে না মিলে যায়)
    deal_key = f"deal_{flash_deal.id}"
    
    if deal_key in cart:
        cart[deal_key]['qty'] += 1
    else:
        # এখানে দামটা তুমি তোমার ডিল অনুযায়ী সেট করে দিবে (যেমন ৯৯৯ টাকা)
        cart[deal_key] = {
            'product_id': flash_deal.id,
            'name': flash_deal.title,
            'price': 999.0, # অথবা flash_deal মডেলে একটা price ফিল্ড নিতে পারো
            'qty': 1,
            'image': flash_deal.image.url if flash_deal.image else '',
            'is_deal': True
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"{flash_deal.title} added to your bag!")
    return redirect('home') # সরাসরি কার্ট পেজে নিয়ে যাবে


def wishlist_page(request):
    wishlist_ids = request.session.get('wishlist', [])
    # আইডিগুলো দিয়ে ডাটাবেস থেকে খাবারগুলো নিয়ে আসা
    wishlist_items = Food.objects.filter(id__in=wishlist_ids)
    
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

def toggle_wishlist(request, food_id):
    # সেশন থেকে বর্তমান উইশলিস্ট লিস্টটি নাও, না থাকলে খালি লিস্ট [] নাও
    wishlist = request.session.get('wishlist', [])
    food_id_str = str(food_id)
    
    if food_id_str in wishlist:
        wishlist.remove(food_id_str) # অলরেডি থাকলে রিমুভ করবে
    else:
        wishlist.append(food_id_str) # না থাকলে অ্যাড করবে
    
    request.session['wishlist'] = wishlist
    request.session.modified = True
    
    # ইউজার যে পেজ থেকে ক্লিক করেছে তাকে সেখানেই ফেরত পাঠাও
    return redirect(request.META.get('HTTP_REFERER', 'menu'))


def food_detail(request, food_id):
    food = get_object_or_404(Food, id=food_id)
    
    # AI সাজেশন্স নিয়ে আসা
    recommendations = get_ai_recommendations(food)
    
    return render(request, 'menu/food_detail.html', {
        'food': food,
        'recommendations': recommendations
    })