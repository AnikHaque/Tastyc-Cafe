import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from orders.models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_payment_intent(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    intent = stripe.PaymentIntent.create(
        amount=int(order.total_price * 100),  # cents
        currency='usd',
        metadata={'order_id': order.id}
    )

    order.stripe_payment_intent = intent.id
    order.save()

    return JsonResponse({
        'client_secret': intent.client_secret,
        'public_key': settings.STRIPE_PUBLIC_KEY
    })
