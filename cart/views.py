from django.shortcuts import render, redirect, get_object_or_404
from menu.models import Food


def cart_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())

    return render(request, 'cart/cart.html', {
        'cart': cart,
        'total': total
    })


def add_to_cart(request, food_id):
    cart = request.session.get('cart', {})
    food = get_object_or_404(Food, id=food_id)

    food_id = str(food_id)

    if food_id in cart:
        cart[food_id]['qty'] += 1
    else:
        cart[food_id] = {
            'name': food.name,
            'price': float(food.price),
            'qty': 1,
            'image': food.image.url
        }

    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, food_id):
    cart = request.session.get('cart', {})
    food_id = str(food_id)

    if food_id in cart:
        del cart[food_id]

    request.session['cart'] = cart
    return redirect('cart')


def update_cart(request, food_id, action):
    cart = request.session.get('cart', {})
    food_id = str(food_id)

    if food_id in cart:
        if action == 'increase':
            cart[food_id]['qty'] += 1
        elif action == 'decrease':
            cart[food_id]['qty'] -= 1

            if cart[food_id]['qty'] <= 0:
                del cart[food_id]

    request.session['cart'] = cart
    return redirect('cart')
