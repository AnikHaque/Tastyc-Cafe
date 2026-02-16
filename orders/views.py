from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from menu.models import Food
from django.contrib.auth.models import User, Group

@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('menu')

    # পাইথন জেনারেটর এক্সপ্রেশন ব্যবহার (Better performance)
    total = sum(float(item['price']) * int(item['qty']) for item in cart.values())

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # অর্ডার ক্রিয়েট
        order = Order.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            total_price=total,
            status='PENDING'
        )

        # পাইথন লজিক দিয়ে আইটেম সেভ করা (Error Fix)
        for item_id, item in cart.items():
            is_combo = str(item_id).startswith('combo_')
            
            # এরর ফিক্স: মডেলে যা আছে ঠিক তাই পাঠানো হচ্ছে (combo সরিয়ে combo_id করা হলো)
            OrderItem.objects.create(
                order=order,
                food_id=None if is_combo else int(item_id),
                combo_id=int(item['product_id']) if is_combo else None,
                price=item['price'],
                quantity=item['qty']
            )

        # অটো-অ্যাসাইন লজিক কল করা (পাইথন শেয়ার বাড়ানোর জন্য)
        try:
            auto_assign_delivery_man(order)
        except Exception as e:
            print(f"Auto-assign error: {e}") # ডেলিভারি ম্যান না থাকলে যেন অর্ডার আটকে না যায়

        request.session['cart'] = {}
        messages.success(request, "অর্ডারটি সফলভাবে সম্পন্ন হয়েছে!")
        
        # পেমেন্ট মেথড অনুযায়ী ডিসিশন
        payment_method = request.POST.get('payment_method')
        if payment_method == 'cod':
            return redirect('my_orders')
        return redirect('payment_page', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'total': total
    })

from django.contrib.auth.decorators import user_passes_test

def is_delivery_man(user):
    return user.groups.filter(name='Delivery Man').exists()

@login_required
@user_passes_test(is_delivery_man, login_url='home')
def delivery_dashboard(request):
    # শুধু এই ডেলিভারি ম্যানকে অ্যাসাইন করা অর্ডারগুলো
    orders = Order.objects.filter(delivery_man=request.user).exclude(status='DELIVERED').order_by('-created_at')
    return render(request, 'delivery/dashboard.html', {'orders': orders})

@login_required
@user_passes_test(is_delivery_man)
def update_delivery_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id, delivery_man=request.user)
    if new_status in ['ON_THE_WAY', 'DELIVERED']:
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {new_status}")
    return redirect('delivery_dashboard')

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Stripe checkout এ redirect
    return redirect('create_payment', order_id=order.id)


@login_required
def payment_success(request):
    return render(request, 'orders/success.html')

@login_required
def my_orders(request):
    # Logged-in user er sob orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'orders/my_orders.html', {
        'orders': orders
    })


@login_required
def mark_paid(request, order_id):
    if not request.user.is_staff:
        messages.error(request, "You are not authorized.")
        return redirect('dashboard')

    order = get_object_or_404(Order, id=order_id)
    order.status = 'PAID'
    order.save()

    messages.success(request, f"Order #{order.id} marked as PAID.")
    return redirect('staff_dashboard')


def delete_order(request, order_id):
    # এখানে get_object_or_404 ব্যবহার করলে শুধু ওই আইডিটাই ধরা পড়বে
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        order.delete() # শুধুমাত্র এই অর্ডারটি ডিলিট হবে
        messages.success(request, f"Order #{order_id} has been deleted.")
    
    return redirect('customer_dashboard')

@login_required
def track_order(request, order_id):
    # কাস্টমার যেন শুধু তার নিজের অর্ডারই ট্র্যাক করতে পারে
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # ডেলিভারি ম্যানের তথ্যসহ অর্ডার আইটেমগুলোও নিচ্ছি
    items = OrderItem.objects.filter(order=order)
    
    return render(request, 'orders/track_order.html', {
        'order': order,
        'items': items
    })


def auto_assign_delivery_man(order):
    """
    পাইথন লজিক যা সবচেয়ে কম কাজ থাকা ডেলিভারি ম্যানকে খুঁজে বের করে
    """
    delivery_group = Group.objects.get(name='Delivery Man')
    delivery_men = User.objects.filter(groups=delivery_group)
    
    # পাইথন লিস্ট কমপ্রিহেনশন এবং সর্টিং লজিক
    worker_loads = [
        {
            'user': man, 
            'count': Order.objects.filter(delivery_man=man, status='ON_THE_WAY').count()
        } 
        for man in delivery_men
    ]
    
    # যার কাজ সবচেয়ে কম তাকেই অ্যাসাইন করবে
    best_man = min(worker_loads, key=lambda x: x['count'])
    
    order.delivery_man = best_man['user']
    order.save()
    return best_man['user']