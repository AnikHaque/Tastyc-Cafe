from django.contrib.auth.decorators import user_passes_test

def staff_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and
                  u.groups.filter(name='Staff').exists()
    )(view_func)


def manager_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and
                  u.groups.filter(name='Manager').exists()
    )(view_func)
