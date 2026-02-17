
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Order, OrderItem
from menu.models import Food
from django.contrib.auth.models import User, Group
from decimal import Decimal

# -------------------------------------------------------------------
# ১. হেল্পার: ডেলিভারি ম্যান চেক
# -------------------------------------------------------------------
def is_delivery_man(user):
    return user.groups.filter(name='Delivery Man').exists()

# -------------------------------------------------------------------
# ২. চেকআউট: পেমেন্ট মেথড অনুযায়ী লজিক
# -------------------------------------------------------------------
@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "আপনার কার্টটি খালি!")
        return redirect('menu')

    total = sum(Decimal(str(item['price'])) * int(item['qty']) for item in cart.values())

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # অর্ডার ক্রিয়েট
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            total_price=total,
            status='PENDING',
            is_paid=False # ডিফল্ট আনপেইড
        )

        for item_id, item_data in cart.items():
            is_combo = str(item_id).startswith('combo_')
            OrderItem.objects.create(
                order=order,
                food_id=None if is_combo else int(item_id),
                combo_id=int(item_data['product_id']) if is_combo else None,
                price=item_data['price'],
                quantity=item_data['qty']
            )

        # ডেলিভারি ম্যান অ্যাসাইন
        try:
            auto_assign_delivery_man(order)
        except:
            pass

        request.session['cart'] = {}
        
        # পেমেন্ট মেথড অনুযায়ী রিডাইরেক্ট
        if payment_method == 'cod':
            messages.success(request, "অর্ডারটি সফল হয়েছে (Cash on Delivery)")
            return redirect('my_orders')
        else:
            # অনলাইন পেমেন্টের জন্য পেমেন্ট পেজে পাঠানো
            return redirect('payment_page', order_id=order.id)

    return render(request, 'orders/checkout.html', {'cart': cart, 'total': total})

# -------------------------------------------------------------------
# ৩. স্টাফ অ্যাকশন: "Confirm & Prepare" (আগের Mark Paid এর পরিবর্তে)
# -------------------------------------------------------------------
@login_required
def mark_paid(request, order_id):
    """
    এখন এটি পেমেন্টের চেয়ে 'অর্ডার কনফার্মেশন' হিসেবে কাজ করবে।
    স্টাফ ক্লিক করলে স্ট্যাটাস PENDING থেকে PREPARING হবে।
    """
    if not request.user.is_staff:
        return redirect('dashboard')

    order = get_object_or_404(Order, id=order_id)
    
    if order.status == 'PENDING':
        order.status = 'PREPARING'
        order.save()
        messages.success(request, f"অর্ডার #{order.id} কনফার্ম করা হয়েছে এবং রান্না শুরু হয়েছে।")
    
    return redirect('staff_dashboard')

# -------------------------------------------------------------------
# ৪. ডেলিভারি ড্যাশবোর্ড: ডেলিভারি হলে অটো পেমেন্ট ট্রু হবে (COD এর জন্য)
# -------------------------------------------------------------------
@login_required
@user_passes_test(is_delivery_man)
def update_delivery_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id, delivery_man=request.user)
    
    # পাইথন লজিক: যদি স্ট্যাটাস ডেলিভারড হয়, তবে পেমেন্টও ট্রু করে দাও
    if new_status == 'DELIVERED':
        order.status = 'DELIVERED'
        order.is_paid = True 
        messages.success(request, f"অর্ডার #{order.id} ডেলিভারড এবং পেমেন্ট সম্পন্ন।")
    elif new_status in ['ON_THE_WAY', 'PREPARING']:
        order.status = new_status
    
    order.save()
    return redirect('delivery_dashboard')

# -------------------------------------------------------------------
# ৫. পেমেন্ট সাকসেস: অনলাইন পেমেন্ট সফল হলে অটো পেমেন্ট ট্রু হবে
# -------------------------------------------------------------------
@login_required
def payment_success(request):
    """
    আপনার পেমেন্ট গেটওয়ে (Stripe/SSL) থেকে যখন এখানে ফিরে আসবে, 
    তখন সেশন বা আইডি চেক করে ইজ পেইড ট্রু করা হয়।
    """
    # এখানে লজিক থাকতে হবে কোন অর্ডারটি পেইড হলো (Session বা URL Parameter থেকে)
    # উদাহরণস্বরূপ আমরা কাস্টমারের শেষ আনপেইড অর্ডারটি ধরছি:
    last_order = Order.objects.filter(user=request.user, is_paid=False).first()
    if last_order:
        last_order.is_paid = True
        last_order.status = 'PREPARING' # অনলাইন পেইড মানেই কনফার্মড অর্ডার
        last_order.save()
        
    return render(request, 'orders/success.html')

# -------------------------------------------------------------------
# অন্যান্য ভিউ (ট্র্যাকিং ও ড্যাশবোর্ড)
# -------------------------------------------------------------------
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

from django.utils import timezone  # এই ইমপোর্টটি ফাইলের একদম উপরে নিশ্চিত করুন

@login_required
def delivery_dashboard(request):
    # শুধুমাত্র এই ডেলিভারি ম্যানের কাছে থাকা একটিভ অর্ডার (Preparing বা On the way)
    orders = Order.objects.filter(
        delivery_man=request.user, 
        status__in=['PREPARING', 'ON_THE_WAY']
    ).order_by('-created_at')
    
    # আজকের তারিখ বের করার সঠিক উপায়
    today = timezone.now().date()
    
    # আজকের সাকসেসফুল ডেলিভারি সংখ্যা
    completed_today = Order.objects.filter(
        delivery_man=request.user, 
        status='DELIVERED', 
        updated_at__date=today
    )
    
    # ইনকাম ক্যালকুলেশন (প্রতি ডেলিভারি ৫০ টাকা হিসেবে)
    total_earnings = completed_today.count() * 50

    return render(request, 'delivery/dashboard.html', {
        'orders': orders,
        'completed_count': completed_today.count(),
        'total_earnings': total_earnings
    })

@login_required
def update_order_status(request, order_id, status):
    """ডেলিভারি ম্যান অর্ডারের স্ট্যাটাস আপডেট করবে"""
    # নিরাপত্তা নিশ্চিত করা: অর্ডারটি যেন এই ডেলিভারি ম্যানেরই হয়
    order = get_object_or_404(Order, id=order_id, delivery_man=request.user)
    
    if status in ['ON_THE_WAY', 'DELIVERED']:
        order.status = status
        order.save()
        
    return redirect('delivery_dashboard')

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return redirect('create_payment', order_id=order.id)
    

@login_required
def delete_order(request, order_id):
    """অর্ডার ডিলিট করার লজিক"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f"Order #{order_id} has been deleted.")
    return redirect('customer_dashboard')


def mark_paid(request, order_id):
    """
    স্টাফ যখন 'Confirm Payment' বা 'Cook Now' বাটনে ক্লিক করবে, তখন এই ফাংশনটি কল হবে।
    এটি পেমেন্ট কনফার্ম করবে এবং রান্নার প্রসেস শুরু করবে।
    """
    # অর্ডারের আইডি দিয়ে অবজেক্টটি খুঁজে বের করা
    order = get_object_or_404(Order, id=order_id)
    
    # পেমেন্ট স্ট্যাটাস আপডেট
    order.is_paid = True 
    
    # যদি অর্ডারটি একদম নতুন (PENDING) থাকে, তবে সেটির প্রসেস শুরু করা (PREPARING)
    if order.status == 'PENDING':
        order.status = 'PREPARING'
    
    order.save()
    
    # কাজ শেষ করে আবার স্টাফ ড্যাশবোর্ডেই ফেরত পাঠানো
    return redirect('staff_dashboard')

