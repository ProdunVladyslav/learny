from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import SESSION_KEY

from apps.accounts.use_cases import LogoutUseCase

User = get_user_model()


class TestLogoutUseCase(TestCase):

    def setUp(self):
        self.factory  = RequestFactory()
        self.use_case = LogoutUseCase()

        self.user = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='SecurePass123!',
        )

    def test_logout_clears_session(self):
        """
        After execute() the user's session is flushed.
        Uses Django test client (not RequestFactory) because
        client properly sets up session middleware.
        """
        # log in via test client — sets up full session
        self.client.login(username='john', password='SecurePass123!')
        self.assertIn('_auth_user_id', self.client.session)

        # call logout through the view (which calls the use case)
        self.client.get('/logout/')

        # session should no longer contain auth data
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_execute_does_not_raise(self):
        """
        execute() on an unauthenticated request should not raise.
        Django's logout() is safe to call even when no user is logged in.
        """
        request = self.factory.post('/logout/')

        # attach a minimal session — RequestFactory doesn't add one
        request.session = {}

        # attach anonymous user
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        try:
            self.use_case.execute(request)
        except Exception as e:
            self.fail(f"LogoutUseCase.execute() raised unexpectedly: {e}")

    def test_logout_returns_none(self):
        """execute() has no return value — it's a void operation."""
        request = self.factory.post('/logout/')
        request.session = {}

        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()

        result = self.use_case.execute(request)
        self.assertIsNone(result)