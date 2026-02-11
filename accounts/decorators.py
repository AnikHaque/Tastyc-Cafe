# accounts/decorators.py
from django.contrib.auth.decorators import user_passes_test

def customer_required(view_func):
    return user_passes_test(lambda u: u.role == 'CUSTOMER')(view_func)

def staff_required(view_func):
    return user_passes_test(lambda u: u.role == 'STAFF')(view_func)

def manager_required(view_func):
    return user_passes_test(lambda u: u.role == 'MANAGER')(view_func)
