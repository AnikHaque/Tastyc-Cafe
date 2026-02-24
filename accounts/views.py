import json
import random
from datetime import date, timedelta, datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils.text import slugify
from django.utils import timezone
from menu.models import Food, Testimonial
from .forms import CustomerRegisterForm, LoginForm, ProfileUpdateForm
from .decorators import customer_required, staff_required, manager_required
from orders.models import Order, OrderItem
from blog.models import Blog 
from accounts.models import UserProfile 
from django.db.models.functions import ExtractHour

# -------------------------------------------------------------------
# ০. Business Intelligence Engine (The Giant Unique Feature)
# -------------------------------------------------------------------
class BusinessIntelligence:
    @staticmethod
    def get_revenue_report():
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        # ১. আজকের রিয়েল-টাইম রেভিনিউ
        daily_sales = Order.objects.filter(
            created_at__date=today, 
            is_paid=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

        # ২. গত ৭ দিনের গড় (Growth Comparison এর জন্য)
        weekly_total = Order.objects.filter(
            created_at__date__range=[week_ago, today], 
            is_paid=True
        ).aggregate(total=Sum('total_price'))['total'] or 0
        weekly_avg = weekly_total / 7

        # ৩. সেলস ভেলোসিটি (শেষ ১ ঘণ্টায় অর্ডার সংখ্যা)
        one_hour_ago = timezone.now() - timedelta(hours=1)
        velocity_count = Order.objects.filter(created_at__gte=one_hour_ago).count()

        # ৪. কাস্টমার লয়্যালটি ইনডেক্স
        total_users = UserProfile.objects.count()
        repeat_customers = Order.objects.values('user').annotate(cnt=Count('id')).filter(cnt__gt=1).count()
        loyalty_score = (repeat_customers / total_users * 100) if total_users > 0 else 0

        return {
            'daily_revenue': daily_sales,
            'growth_index': daily_sales > weekly_avg,
            'velocity_per_hour': velocity_count,
            'loyalty_index': round(loyalty_score, 1)
        }

# -------------------------------
# ১. Intelligence Dashboard View
# -------------------------------
@login_required
def admin_intelligence_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')
        
    report = BusinessIntelligence.get_revenue_report()
    
    # টপ সেলিং খাবারগুলো
    top_items = OrderItem.objects.values('food__name').annotate(
        sold_qty=Sum('quantity')
    ).order_by('-sold_qty')[:5]

    # লো স্টক আইটেম সংখ্যা
    low_stock_count = Food.objects.filter(stock__lte=5, is_available=True).count()

    context = {
        'report': report,
        'top_items': top_items,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'accounts/dashboard/admin_intelligence.html', context)

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
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
@login_required
def customer_dashboard(request):
    if request.user.is_staff:
        return redirect('staff_dashboard')
    from .dashboard_logic import CustomerAnalytics
    analytics = CustomerAnalytics(user=request.user, order_model=Order, review_model=Testimonial)
    context = analytics.get_all_stats()

    # ২. লয়্যালটি লজিক (সরাসরি ভিউতে)
    completed_order_count = Order.objects.filter(user=request.user, status__iexact='Completed').count()
    
    # টায়ার কনফিগারেশন
    TIERS = {
        'BRONZE': {'min_orders': 0, 'discount': 0, 'badge': '🥉', 'next': 5},
        'SILVER': {'min_orders': 5, 'discount': 5, 'badge': '🥈', 'next': 15},
        'GOLD': {'min_orders': 15, 'discount': 10, 'badge': '🥇', 'next': None},
    }

    # বর্তমান টায়ার বের করা
    if completed_order_count >= TIERS['GOLD']['min_orders']:
        tier_key = 'GOLD'
    elif completed_order_count >= TIERS['SILVER']['min_orders']:
        tier_key = 'SILVER'
    else:
        tier_key = 'BRONZE'

    current_tier = TIERS[tier_key]
    
    # পরবর্তী লেভেলের প্রগ্রেস ক্যালকুলেশন
    next_goal = current_tier['next']
    if next_goal:
        remaining = next_goal - completed_order_count
        # প্রগ্রেস বার এর জন্য পার্সেন্টেজ (ম্যাক্সিমাম ১০০%)
        progress = (completed_order_count / next_goal) * 100
    else:
        remaining = 0
        progress = 100

    # ৩. কন্টেক্সটে আলাদা করে লয়্যালটি ডাটা পুশ করা
    context['loyalty'] = {
        'tier_name': tier_key,
        'tier_badge': current_tier['badge'],
        'discount': current_tier['discount'],
        'completed_count': completed_order_count,
        'remaining': remaining,
        'progress_percent': round(progress, 1),
        'is_gold': tier_key == 'GOLD'
    }
    return render(request, 'accounts/dashboard/customer_dashboard.html', context)

# -------------------------------
# Staff Dashboard & Analytics
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
    
    # ৭ দিনের রেভিনিউ এবং অর্ডারের সংখ্যা একসাথে আনা
    analytics_qs = (
        Order.objects.filter(created_at__date__gte=last_week)
        .values('created_at__date')
        .annotate(
            total_rev=Sum('total_price'),
            order_count=Count('id')
        )
        .order_by('created_at__date')
    )

    # জ্যাসন ডাটা তৈরি (যাতে চার্ট কখনো এরর না দেয়)
    labels = []
    revenue_data = []
    orders_count_data = []

    # গত ৭ দিনের প্রতিটা দিনের জন্য ডাটা সেট করা (কোনো দিন অর্ডার না থাকলে ০ দেখাবে)
    for i in range(7):
        curr_date = last_week + timedelta(days=i)
        labels.append(curr_date.strftime('%d %b'))
        
        # ডাটাবেজের রেজাল্ট থেকে ওই দিনের ডাটা খুঁজে বের করা
        day_data = next((item for item in analytics_qs if item['created_at__date'] == curr_date), None)
        
        if day_data:
            revenue_data.append(float(day_data['total_rev'] or 0))
            orders_count_data.append(day_data['order_count'] or 0)
        else:
            revenue_data.append(0)
            orders_count_data.append(0)

    context = {
        'total_orders': Order.objects.count(),
        'total_paid': Order.objects.filter(is_paid=True).count(),
        'total_pending': Order.objects.filter(is_paid=False).count(),
        # json.dumps ব্যবহার করলে জাভাস্ক্রিপ্ট এরর হওয়ার সুযোগ থাকে না
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(revenue_data),
        'orders_per_day': json.dumps(orders_count_data), 
    }
    return render(request, 'accounts/dashboard/staff_analytics.html', context)
@login_required
def staff_operation_pulse(request):
    if not request.user.is_staff:
        return redirect('home')

    # ২৪ ঘণ্টার ডাটা আনা
    peak_hours_qs = Order.objects.annotate(
        hour=ExtractHour('created_at')
    ).values('hour').annotate(count=Count('id')).order_by('hour')

    hour_labels = [f"{h}:00" for h in range(24)]
    hour_data = [0] * 24
    for item in peak_hours_qs:
        hour_data[item['hour']] = item['count']

    # ব্যস্ততম সময় এবং প্রেডিকশন
    max_orders = max(hour_data) if hour_data else 0
    busy_hour = hour_labels[hour_data.index(max_orders)] if max_orders > 0 else "N/A"

    context = {
        'hour_labels': json.dumps(hour_labels),
        'hour_data': json.dumps(hour_data),
        'busy_hour': busy_hour,
        'total_insights': sum(hour_data)
    }
    return render(request, 'accounts/dashboard/staff_operation_pulse.html', context)

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
# Actions
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

@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_settings')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/dashboard/profile_settings.html', {'form': form})

def support_page(request):
    # একদম সিম্পল ভিউ যা শুধু একটি পেজ দেখাবে
    return render(request, 'accounts/dashboard/support.html')