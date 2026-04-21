from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('access_token')

        if token:
            try:
                validated = AccessToken(token)
                user_id   = validated['user_id']
                request.user = User.objects.get(id=user_id)
            except (InvalidToken, TokenError, User.DoesNotExist):
                request.user = AnonymousUser()
        # ← no else branch — let AuthenticationMiddleware handle it

        return self.get_response(request)