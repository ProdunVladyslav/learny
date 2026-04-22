from rest_framework_simplejwt.tokens import RefreshToken

from config import settings


class TokenService:
    """
    Infrastructure service — manages JWT token generation and cookie attachment.
    Lives in services/ not domain_services/ because it's infrastructure:
    it knows about HTTP cookies, JWT library, and settings.
    Domain services know none of that.
    """

    ACCESS_TOKEN_MAX_AGE  = 60 * 15            # 15 minutes
    REFRESH_TOKEN_MAX_AGE = 60 * 60 * 24 * 14  # 14 days

    @staticmethod
    def generate_tokens(user) -> tuple[str, str]:
        """Returns (access_token, refresh_token) as strings."""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)

    @classmethod
    def set_auth_cookies(
        cls,
        response,
        access:      str,
        refresh:     str,
        remember_me: bool = True,
    ) -> None:
        """Attaches JWT tokens as HttpOnly cookies to the response."""
        response.set_cookie(
            'access_token',
            access,
            max_age=cls.ACCESS_TOKEN_MAX_AGE,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
        )
        response.set_cookie(
            'refresh_token',
            refresh,
            max_age=cls.REFRESH_TOKEN_MAX_AGE if remember_me else None,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
        )

    @staticmethod
    def clear_auth_cookies(response) -> None:
        """Clears JWT cookies — called on logout."""
        for cookie in ('access_token', 'refresh_token'):
            response.set_cookie(cookie, '', max_age=0, path='/', httponly=True, samesite='Lax')