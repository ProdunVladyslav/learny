from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class SignupForm(UserCreationForm):
    email       = forms.EmailField(required=True)
    remember_me = forms.BooleanField(required=False)

    class Meta:
        model  = User
        fields = ['email', 'username', 'password1', 'password2']