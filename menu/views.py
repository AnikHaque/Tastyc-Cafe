from django.shortcuts import render, get_object_or_404,redirect
from .models import Category, ComboDeal, Testimonial
from django.contrib import messages
# আগের ইমপোর্টের সাথে শুধু ComboDeal টা কমা দিয়ে যোগ করে দিন


def menu_view(request):
    categories = Category.objects.prefetch_related('foods')
    return render(request, 'menu.html', {'categories': categories})


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


