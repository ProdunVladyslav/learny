from django.contrib.auth import logout as django_logout


class LogoutUseCase:
    """
    Terminates the Django session.
    Cookie clearing is an HTTP concern — handled by the view after execute().
    No repo needed — Django's logout() manages session state internally.
    """

    def execute(self, request) -> None:
        django_logout(request)