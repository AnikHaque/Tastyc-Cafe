from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from menu.models import Food, Testimonial
from .forms import CustomerRegisterForm, LoginForm
from .decorators import customer_required, staff_required, manager_required
from orders.models import Order, OrderItem
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
import json
from datetime import date, timedelta, datetime
from blog.models import Blog 
from django.utils.text import slugify



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
            user.is_staff = False
            user.save()
            login(request, user)
            messages.success(request, 'Account created successfully')
            return redirect('menu')
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
            return redirect('staff_dashboard' if request.user.is_staff else 'home')
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
from .dashboard_logic import CustomerAnalytics

@login_required
def customer_dashboard(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
    analytics = CustomerAnalytics(user=request.user, order_model=Order, review_model=Testimonial)
    context = analytics.get_all_stats()
    return render(request, 'accounts/dashboard/customer_dashboard.html', context)

# -------------------------------
# Staff Dashboard & Analytics (Fixing the Errors)
# -------------------------------

@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment')
    view_type = request.GET.get('view', 'orders')

    orders = Order.objects.all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    if payment_filter == 'PAID':
        orders = orders.filter(is_paid=True)
    elif payment_filter == 'UNPAID':
        orders = orders.filter(is_paid=False)

    context = {
        'orders': orders.order_by('-created_at'),
        'total_orders': Order.objects.count(),
        'total_paid': Order.objects.filter(is_paid=True).count(),
        'total_pending': Order.objects.filter(is_paid=False).count(),
        'view_type': view_type,
    }
    return render(request, 'accounts/dashboard/staff_dashboard.html', context)

@login_required
def staff_analytics(request):
    if not request.user.is_staff:
        return redirect('home')
    
    last_week = date.today() - timedelta(days=6)
    revenue_qs = (
        Order.objects.filter(created_at__date__gte=last_week, is_paid=True)
        .values('created_at__date')
        .annotate(total=Sum('total_price'))
        .order_by('created_at__date')
    )

    context = {
        'total_orders': Order.objects.count(),
        'total_paid': Order.objects.filter(is_paid=True).count(),
        'total_pending': Order.objects.filter(is_paid=False).count(),
        'chart_labels': [d['created_at__date'].strftime('%d %b') for d in revenue_qs],
        'chart_data': [float(d['total']) for d in revenue_qs],
    }
    return render(request, 'accounts/dashboard/staff_analytics.html', context)

@login_required
def staff_inventory(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    low_stock_items = Food.objects.filter(stock__lte=5, is_available=True)
    return render(request, 'accounts/dashboard/staff_inventory.html', {'low_stock_items': low_stock_items})

@login_required
def staff_top_selling(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    last_month = datetime.today() - timedelta(days=30)
    top_selling_qs = (
        OrderItem.objects.filter(order__created_at__gte=last_month)
        .values('food__name')
        .annotate(sales_count=Count('id'))
        .order_by('-sales_count')[:10]
    )
    top_selling = [{'food_name': item['food__name'], 'sales_count': item['sales_count']} for item in top_selling_qs]
    context = {
        'top_selling': top_selling,
        'top_selling_labels': [item['food_name'] for item in top_selling],
        'top_selling_data': [item['sales_count'] for item in top_selling],
    }
    return render(request, 'accounts/dashboard/staff_top_selling.html', context)

# -------------------------------
# Reservations & Actions
# -------------------------------




@login_required
@staff_required
def mark_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_paid = True
    order.status = 'PREPARING'
    order.save()
    messages.success(request, f'Order #{order.id} marked as Paid & Preparing')
    return redirect('staff_dashboard')

# -------------------------------
# Blog Management
# -------------------------------

@login_required
def staff_blog_list(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'accounts/dashboard/staff_blog_list.html', {'blogs': blogs})

@login_required
def staff_create_blog(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    if request.method == 'POST':
        title = request.POST.get('title')
        Blog.objects.create(
            title=title, slug=slugify(title), content=request.POST.get('content'),
            category=request.POST.get('category'), read_time=request.POST.get('read_time', 5),
            tags=request.POST.get('tags', ''), thumbnail=request.FILES.get('thumbnail'),
            author=request.user, is_published=True
        )
        return redirect('staff_blog_list') 
    return render(request, 'accounts/dashboard/staff_create_blog.html')

def staff_edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == "POST":
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        if request.FILES.get('thumbnail'):
            blog.thumbnail = request.FILES.get('thumbnail')
        blog.save()
        return redirect('staff_blog_list')
    return render(request, 'accounts/dashboard/staff_create_blog.html', {'blog': blog, 'edit_mode': True})

def staff_delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == "POST":
        blog.delete()
    return redirect('staff_blog_list')




