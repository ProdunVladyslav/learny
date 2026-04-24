from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'{reverse("accounts:login")}?next={request.path}')
        return view_func(request, *args, **kwargs)
    return wrapper