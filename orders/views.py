import random
import time
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User, Group
from decimal import Decimal

from accounts.models import UserProfile
from .models import Order, OrderItem
from menu.models import Food

# -------------------------------------------------------------------
# ১. হেল্পার: ডেলিভারি ম্যান চেক
# -------------------------------------------------------------------
def is_delivery_man(user):
    return user.groups.filter(name='Delivery Man').exists()

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "আপনার কার্টটি খালি!")
        return redirect('menu')

    # কার্টের বেস টোটাল
    total = sum(Decimal(str(item['price'])) * int(item['qty']) for item in cart.values())
    
    # --- কুপন লজিক শুরু ---
    discount_amount = Decimal('0.00')
    coupon_code = request.session.get('applied_coupon')
    discount_percent = request.session.get('discount_percent')

    if coupon_code and discount_percent:
        discount_amount = (total * Decimal(str(discount_percent))) / 100
        total = total - discount_amount # ডিসকাউন্ট বাদ দিয়ে ফাইনাল টোটাল
    # --- কুপন লজিক শেষ ---

    if request.method == 'POST':
        # ডাবল সাবমিট প্রোটেকশন
        last_order_time = request.session.get('last_order_time', 0)
        if time.time() - last_order_time < 60:
            messages.error(request, "একটু অপেক্ষা করুন! আপনি মাত্র একটি অর্ডার দিয়েছেন।")
            return redirect('my_orders')

        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        try:
            with transaction.atomic():
                # রিয়েল-টাইম স্টক গার্ড (আপনার আগের কোড অনুযায়ী)
                for item_id, item_data in cart.items():
                    if not str(item_id).startswith('combo_') and not str(item_id).startswith('deal_'):
                        food = Food.objects.select_for_update().get(id=int(item_id))
                        if food.stock < int(item_data['qty']):
                            messages.error(request, f"দুঃখিত, {food.name} পর্যাপ্ত স্টকে নেই।")
                            return redirect('menu')
                        food.stock -= int(item_data['qty'])
                        food.save()

                # অর্ডার ক্রিয়েট (নতুন কুপন ফিল্ড সহ)
                order = Order.objects.create(
                    user=request.user,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    total_price=total,       # এটি এখন ডিসকাউন্ট করা প্রাইস
                    coupon_code=coupon_code, # সেশন থেকে নেওয়া
                    discount_amount=discount_amount, # ক্যালকুলেট করা অ্যামাউন্ট
                    status='PENDING',
                    is_paid=False 
                )

                # OrderItem ক্রিয়েট করা (আপনার আগের কোড)
                for item_id, item_data in cart.items():
                    is_combo = str(item_id).startswith('combo_')
                    OrderItem.objects.create(
                        order=order,
                        food_id=None if is_combo else int(item_id),
                        combo_id=int(item_data['product_id']) if is_combo else None,
                        price=item_data['price'],
                        quantity=item_data['qty']
                    )

                # সেশন ক্লিনআপ
                request.session['last_order_time'] = time.time()
                request.session['cart'] = {}
                if 'applied_coupon' in request.session:
                    del request.session['applied_coupon']
                    del request.session['discount_percent']

                try:
                    auto_assign_delivery_man(order)
                except: pass

                if payment_method == 'cod':
                    messages.success(request, f"অর্ডার সফল হয়েছে! আপনি ৳{discount_amount} ডিসকাউন্ট পেয়েছেন।")
                    return redirect('my_orders')
                else:
                    return redirect('payment_page', order_id=order.id)

        except Exception as e:
            messages.error(request, f"অর্ডার প্রসেস করার সময় সমস্যা হয়েছে: {str(e)}")
            return redirect('menu')

    return render(request, 'orders/checkout.html', {
        'cart': cart, 
        'total': total, 
        'discount': discount_amount, 
        'original_total': total + discount_amount
    })


# -------------------------------------------------------------------
# ৩. স্টাফ অ্যাকশন: "Confirm & Prepare"
# -------------------------------------------------------------------
@login_required
def mark_paid(request, order_id):
    if not request.user.is_staff:
        return redirect('dashboard')

    order = get_object_or_404(Order, id=order_id)
    order.is_paid = True 
    if order.status == 'PENDING':
        order.status = 'PREPARING'
    order.save()
    messages.success(request, f"অর্ডার #{order.id} কনফার্ম করা হয়েছে।")
    return redirect('staff_dashboard')

# -------------------------------------------------------------------
# ৪. ডেলিভারি ড্যাশবোর্ড লজিক
# -------------------------------------------------------------------
@login_required
@user_passes_test(is_delivery_man)
def update_delivery_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id, delivery_man=request.user)
    
    if new_status == 'DELIVERED':
        order.status = 'DELIVERED'
        order.is_paid = True 
        messages.success(request, f"অর্ডার #{order.id} ডেলিভারড!")
        update_user_rewards(order.user, order.total_price)
    elif new_status in ['ON_THE_WAY', 'PREPARING']:
        order.status = new_status
    
    order.save()
    return redirect('delivery_dashboard')

@login_required
def update_order_status(request, order_id, status):
    order = get_object_or_404(Order, id=order_id, delivery_man=request.user)
    if status in ['ON_THE_WAY', 'DELIVERED']:
        order.status = status
        if status == 'DELIVERED':
            order.is_paid = True
            update_user_rewards(order.user, order.total_price)
        order.save()
    return redirect('delivery_dashboard')

# -------------------------------------------------------------------
# ৫. পেমেন্ট ও অন্যান্য ভিউ
# -------------------------------------------------------------------
@login_required
def payment_success(request):
    last_order = Order.objects.filter(user=request.user, is_paid=False).first()
    if last_order:
        last_order.is_paid = True
        last_order.status = 'PREPARING'
        last_order.save()
        update_user_rewards(request.user, last_order.total_price)
    return render(request, 'orders/success.html')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'orders/track_order.html', {'order': order, 'items': items})

def auto_assign_delivery_man(order):
    try:
        delivery_group = Group.objects.get(name='Delivery Man')
        delivery_men = User.objects.filter(groups=delivery_group)
        if delivery_men.exists():
            worker_loads = [{'user': m, 'count': Order.objects.filter(delivery_man=m, status='ON_THE_WAY').count()} for m in delivery_men]
            best_man = min(worker_loads, key=lambda x: x['count'])
            order.delivery_man = best_man['user']
            order.save()
    except:
        pass

@login_required
def delivery_dashboard(request):
    orders = Order.objects.filter(
        delivery_man=request.user, 
        status__in=['PREPARING', 'ON_THE_WAY']
    ).order_by('-created_at')
    today = timezone.now().date()
    completed_today = Order.objects.filter(
        delivery_man=request.user, 
        status='DELIVERED', 
        updated_at__date=today
    )
    total_earnings = completed_today.count() * 50
    return render(request, 'delivery/dashboard.html', {
        'orders': orders,
        'completed_count': completed_today.count(),
        'total_earnings': total_earnings
    })

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return redirect('create_payment', order_id=order.id)

@login_required
def my_payments(request):
    # আপনার মডেল অনুযায়ী is_paid ফিল্ডটি ব্যবহার করা হয়েছে
    payments = Order.objects.filter(user=request.user, is_paid=True).order_by('-created_at')
    
    return render(request, 'accounts/dashboard/my_payments.html', {'payments': payments})

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f"Order #{order_id} has been deleted.")
    return redirect('customer_dashboard')

# -------------------------------------------------------------------
# ৬. রিওয়ার্ড ও সারপ্রাইজ বক্স
# -------------------------------------------------------------------
def update_user_rewards(user, order_total):
    profile, created = UserProfile.objects.get_or_create(user=user)
    earned_points = int(order_total / 100) * 5
    profile.points += earned_points
    profile.total_orders += 1
    if profile.total_orders >= 20: profile.membership_level = 'Platinum'
    elif profile.total_orders >= 10: profile.membership_level = 'Gold'
    elif profile.total_orders >= 5: profile.membership_level = 'Silver'
    profile.save()


@login_required
def surprise_box_view(request):
    winning_food = None
    if request.method == "POST":
        surprise_items = Food.objects.filter(is_surprise_item=True)
        if not surprise_items.exists():
            surprise_items = Food.objects.all()
        if surprise_items.exists():
            winning_food = random.choice(surprise_items)
            request.session['last_surprise_id'] = winning_food.id
        else:
            messages.error(request, "দুঃখিত, বর্তমানে কোনো সারপ্রাইজ আইটেম নেই।")
    return render(request, 'orders/surprise_box.html', {'winning_food': winning_food})

def reorder_instant(request, order_id):
    """পুরো একটি অর্ডারকে এক ক্লিকে কার্টে কপি করার লজিক"""
    # ১. আগের অর্ডারটি খুঁজে বের করা
    old_order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # ২. বর্তমান সেশন থেকে কার্ট আনা
    cart = request.session.get('cart', {})
    
    # ৩. আগের অর্ডারের সব আইটেম লুপ করে কার্টে ঢুকানো
    # ধরে নিচ্ছি আপনার অর্ডারে 'items' নামে related_name আছে
    for item in old_order.items.all():
        food_id = str(item.food.id)
        if food_id in cart:
            cart[food_id]['qty'] += item.quantity
        else:
            cart[food_id] = {
                'product_id': item.food.id,
                'name': item.food.name,
                'price': float(item.food.price),
                'qty': item.quantity,
                'image': item.food.image.url if item.food.image else ''
            }
    
    # ৪. সেশন সেভ করা
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, f"Order #{old_order.id} items added to cart!")
    return redirect('cart') # সরাসরি কার্ট পেজে নিয়ে যাবে

def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get('coupon_code')
        now = timezone.now()
        try:
            # আমরা আগের মডেলে code, discount, valid_to, active রেখেছিলাম
            from .models import Coupon 
            coupon = Coupon.objects.get(code__iexact=code, valid_to__gte=now, active=True)
            
            request.session['applied_coupon'] = coupon.code
            request.session['discount_percent'] = coupon.discount
            messages.success(request, f'কুপন "{code}" সফলভাবে যোগ করা হয়েছে!')
        except Exception:
            messages.error(request, "দুঃখিত, কুপনটি সঠিক নয় বা মেয়াদ শেষ হয়ে গেছে।")
            
        return redirect(request.META.get('HTTP_REFERER', 'cart'))