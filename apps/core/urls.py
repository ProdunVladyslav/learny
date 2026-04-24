from django.urls import path
from apps.core.views.dashboard_view import dashboard_view
from apps.core.views.welcome_view import welcome_view

app_name = 'core'

urlpatterns = [
    path('', welcome_view, name='welcome'),
    path('dashboard/', dashboard_view, name='dashboard'),
]