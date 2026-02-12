from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from menu.models import Food
from .forms import CustomerRegisterForm, LoginForm
from .decorators import customer_required, staff_required, manager_required
from orders.models import Order
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
import json
from datetime import date, timedelta,datetime
from orders.models import OrderItem
from django.shortcuts import render
from reservations.models import Reservation
# -------------------------------
# Authentication Views
# -------------------------------

def register_view(request):
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # 🔒 Ensure public register = customer
            user.is_staff = False
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('menu')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = CustomerRegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Logged in successfully')

            # Redirect based on role
            if request.user.is_staff:
                return redirect('staff_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('home')


# -------------------------------
# Customer Dashboard
# -------------------------------

@login_required
def dashboard(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
    # normal customer
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/dashboard/customer_dashboard.html', {'orders': orders})

@login_required
def customer_dashboard(request):
    # Normal user orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/dashboard/customer_dashboard.html', {
        'orders': orders
    })

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')

    status_filter = request.GET.get('status')
    if status_filter in ['PAID', 'PENDING']:
        orders = Order.objects.filter(status=status_filter).order_by('-created_at')
    else:
        orders = Order.objects.all().order_by('-created_at')

    return render(request, 'accounts/dashboard/staff_dashboard.html', {
        'orders': orders
    })

@login_required
def staff_inventory(request):
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')

    low_stock_items = Food.objects.filter(stock__lte=5, is_available=True)

    context = {
        'low_stock_items': low_stock_items
    }
    return render(request, 'accounts/dashboard/staff_inventory.html', context)


@login_required
def staff_analytics(request):
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('dashboard')

    # Summary counts
    total_orders = Order.objects.count()
    total_paid = Order.objects.filter(status='PAID').count()
    total_pending = Order.objects.filter(status='PENDING').count()

    # Last 7 days
    last_week = date.today() - timedelta(days=6)  # including today

    # Revenue chart data
    revenue_data_qs = (
        Order.objects.filter(created_at__date__gte=last_week)
        .values('created_at__date')
        .annotate(total=Sum('total_price'))
        .order_by('created_at__date')
    )

    chart_labels = [d['created_at__date'].strftime('%d %b') for d in revenue_data_qs]
    chart_data = [float(d['total']) for d in revenue_data_qs]

    # Orders per day
    orders_data = (
        Order.objects.filter(created_at__date__gte=last_week)
        .values('created_at__date')
        .annotate(count=Count('id'))
        .order_by('created_at__date')
    )
    orders_per_day = [d['count'] for d in orders_data]

    context = {
        'total_orders': total_orders,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'orders_per_day': orders_per_day,
    }

    return render(request, 'accounts/dashboard/staff_analytics.html', context)

@login_required
def staff_top_selling(request):
    if not request.user.is_staff:
        messages.error(request, "Unauthorized access")
        return redirect('dashboard')

    today = datetime.today()
    last_month = today - timedelta(days=30)

    # Top selling dishes last 30 days
    top_selling_qs = (
        OrderItem.objects.filter(order__created_at__gte=last_month)
        .values('food_name')
        .annotate(sales_count=Count('id'))
        .order_by('-sales_count')[:10]
    )

    # Context er jonno list of dict
    top_selling = [{'food_name': item['food_name'], 'sales_count': item['sales_count']} for item in top_selling_qs]

    context = {
        'top_selling': top_selling,
        'top_selling_labels': [item['food_name'] for item in top_selling],
        'top_selling_data': [item['sales_count'] for item in top_selling],
    }

    return render(request, 'accounts/dashboard/staff_top_selling.html', context)

@login_required
def manager_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "You are not authorized.")
        return redirect('dashboard')
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'accounts/dashboard/manager_dashboard.html', {'orders': orders})


# -------------------------------
# Staff Action: Mark Order Paid
# -------------------------------

@login_required
@staff_required
def mark_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'PAID'
    order.save()
    messages.success(request, f'Order #{order.id} marked as Paid')
    return redirect('staff_dashboard')


@login_required
def staff_reservations(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    reservations = Reservation.objects.all().order_by('date', 'time')
    return render(request, 'accounts/dashboard/staff_reservations.html', {'reservations': reservations})

@login_required
def update_reservation_status(request, reservation_id, status):
    if not request.user.is_staff:
        return redirect('dashboard')
    reservation = Reservation.objects.get(id=reservation_id)
    reservation.status = status
    reservation.save()
    return redirect('staff_reservations')
