from django.shortcuts import render, redirect


def welcome_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/welcome.html')