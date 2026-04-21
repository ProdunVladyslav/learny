from django.urls import path

from apps.accounts import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.login_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
]