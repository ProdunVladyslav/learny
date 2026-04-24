from django.urls import path
from apps.accounts import views
from apps.accounts.views import LanguageLearnerCreateView

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('learners/create/', LanguageLearnerCreateView.as_view(), name='add_language'),
]