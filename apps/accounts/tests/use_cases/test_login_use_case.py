"""
apps/accounts/tests/use_cases/test_login_use_case.py

Structure:
  apps/accounts/
  └── tests/
      ├── __init__.py
      ├── use_cases/
      │   ├── __init__.py
      │   ├── test_login_use_case.py   ← this file
      │   ├── test_signup_use_case.py
      │   └── test_logout_use_case.py
      └── models/
          ├── __init__.py
          └── test_custom_user.py      ← your existing model tests go here

Why TestCase and not unittest.TestCase?
  django.test.TestCase wraps each test in a transaction that rolls back.
  DB is clean between tests with zero setup cost.

Why not mock the DB here?
  Use case tests are intentionally NOT pure unit tests.
  They test the full use case contract including real DB interaction.
  If you want pure unit tests without DB, use unittest.TestCase + Mock.
  Both approaches are valid — we use DB-backed tests here because
  the value of a LoginUseCase test is verifying it works end-to-end.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from apps.accounts.repositories import UserRepository
from apps.accounts.use_cases import LoginUseCase
from apps.accounts.use_cases.login_use_case import LoginResult

User = get_user_model()


class TestLoginUseCase(TestCase):

    def setUp(self):
        self.factory    = RequestFactory()
        self.user_repo  = UserRepository()
        self.use_case   = LoginUseCase(user_repo=self.user_repo)

        # create a real user in the test DB
        self.user = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='SecurePass123!',
        )

    # ── Success ───────────────────────────────────────────────────────────────

    def test_login_success_returns_user(self):
        """Correct credentials → success=True, user returned."""
        request = self.factory.post('/login/')

        result = self.use_case.execute(
            request=request,
            username='john',
            password='SecurePass123!',
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.user)
        self.assertEqual(result.user.username, 'john')
        self.assertIsNone(result.error)

    def test_login_success_returns_correct_user_instance(self):
        """Returned user is the same user we created."""
        request = self.factory.post('/login/')

        result = self.use_case.execute(
            request=request,
            username='john',
            password='SecurePass123!',
        )

        self.assertEqual(result.user.id, self.user.id)
        self.assertEqual(result.user.email, 'john@example.com')

    # ── Failure ───────────────────────────────────────────────────────────────

    def test_login_wrong_password_returns_failure(self):
        """Wrong password → success=False, error message set, no user."""
        request = self.factory.post('/login/')

        result = self.use_case.execute(
            request=request,
            username='john',
            password='WrongPassword!',
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.user)
        self.assertEqual(result.error, 'Invalid credentials.')

    def test_login_nonexistent_user_returns_failure(self):
        """Unknown username → success=False, no user."""
        request = self.factory.post('/login/')

        result = self.use_case.execute(
            request=request,
            username='nobody',
            password='SecurePass123!',
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.user)
        self.assertIsNotNone(result.error)

    def test_login_empty_username_returns_failure(self):
        """Empty username → failure, no crash."""
        request = self.factory.post('/login/')

        result = self.use_case.execute(
            request=request,
            username='',
            password='SecurePass123!',
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.user)

    def test_login_empty_password_returns_failure(self):
        """Empty password → failure, no crash."""
        request = self.factory.post('/login/')

        result = self.use_case.execute(
            request=request,
            username='john',
            password='',
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.user)

    def test_login_result_is_login_result_type(self):
        """Result is always a LoginResult dataclass regardless of outcome."""
        request = self.factory.post('/login/')

        result = self.use_case.execute(
            request=request,
            username='john',
            password='bad',
        )

        self.assertIsInstance(result, LoginResult)