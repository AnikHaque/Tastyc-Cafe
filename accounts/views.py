from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CustomerRegisterForm, LoginForm
from .decorators import customer_required, staff_required, manager_required



def register_view(request):
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # 🔒 ensure public register = customer
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
            return redirect('menu')
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




@login_required
@customer_required
def customer_dashboard(request):
    return render(request, 'accounts/customer_dashboard.html')

@login_required
@staff_required
def staff_dashboard(request):
    # Example: show pending orders
    from orders.models import Order
    pending_orders = Order.objects.filter(status='PENDING')
    return render(request, 'accounts/staff_dashboard.html', {'pending_orders': pending_orders})

@login_required
@manager_required
def manager_dashboard(request):
    # Example: show all orders + staff
    from orders.models import Order
    from django.contrib.auth.models import User
    staff_users = User.objects.filter(role='STAFF')
    all_orders = Order.objects.all()
    return render(request, 'accounts/manager_dashboard.html', {
        'all_orders': all_orders,
        'staff_users': staff_users
    })

@login_required
def login_redirect(request):
    if request.user.role == 'CUSTOMER':
        return redirect('customer_dashboard')
    elif request.user.role == 'STAFF':
        return redirect('staff_dashboard')
    elif request.user.role == 'MANAGER':
        return redirect('manager_dashboard')
    return redirect('home')  # fallback