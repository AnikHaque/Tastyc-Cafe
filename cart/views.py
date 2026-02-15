from django.shortcuts import render, redirect, get_object_or_404
from menu.models import Food
from django.contrib import messages

def cart_view(request):
    cart = request.session.get('cart', {})
    
    # সব ভ্যালুকে float এবং int নিশ্চিত করে যোগ করা হচ্ছে যাতে TypeError না আসে
    total = sum(float(item['price']) * int(item['qty']) for item in cart.values())

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'total': total
    })

def add_to_cart(request, food_id):
    cart = request.session.get('cart', {})
    
    # যেহেতু food_id স্ট্রিং হিসেবে আসতে পারে, তাই আইডিটাকে int এ রূপান্তর করে ফুড অবজেক্ট নিচ্ছি
    try:
        food = get_object_or_404(Food, id=int(food_id))
    except ValueError:
        messages.error(request, "Invalid Food ID")
        return redirect('menu')

    item_id = str(food_id)

    if item_id in cart:
        cart[item_id]['qty'] += 1
    else:
        cart[item_id] = {
            'product_id': food.id, # অর্ডারের সময় কাজে লাগবে
            'name': food.name,
            'price': float(food.price),
            'qty': 1,
            'image': food.image.url if food.image else ''
        }

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')

def remove_from_cart(request, food_id):
    cart = request.session.get('cart', {})
    food_id = str(food_id)

    if food_id in cart:
        del cart[food_id]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')

def update_cart(request, food_id, action):
    cart = request.session.get('cart', {})
    food_id = str(food_id)

    if food_id in cart:
        if action == 'increase':
            cart[food_id]['qty'] = int(cart[food_id]['qty']) + 1
        elif action == 'decrease':
            cart[food_id]['qty'] = int(cart[food_id]['qty']) - 1

            if cart[food_id]['qty'] <= 0:
                del cart[food_id]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')