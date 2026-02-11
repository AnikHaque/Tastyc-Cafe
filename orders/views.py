from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem


@login_required
def checkout_view(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('menu')

    total = sum(item['price'] * item['qty'] for item in cart.values())

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_price=total
        )

        for item in cart.values():
            OrderItem.objects.create(
                order=order,
                food_name=item['name'],
                price=item['price'],
                quantity=item['qty']
            )

        request.session['cart'] = {}
        return redirect('payment_page', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'total': total
    })

@login_required
def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/payment.html', {'order': order})

@login_required
def payment_success(request):
    return render(request, 'orders/success.html')
