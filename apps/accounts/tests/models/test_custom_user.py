from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class TestCustomUser(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='SecurePass123!',
        )

    # ── Factory ──────────────────────────────────────────────────────────────

    def test_create_user_saves_to_db(self):
        self.assertIsNotNone(self.user.id)
        self.assertTrue(User.objects.filter(username='john').exists())

    def test_create_user_sets_email(self):
        self.assertEqual(self.user.email, 'john@example.com')

    def test_create_user_hashes_password(self):
        """Password must never be stored in plain text."""
        self.assertNotEqual(self.user.password, 'SecurePass123!')
        self.assertTrue(self.user.check_password('SecurePass123!'))

    def test_str_returns_email(self):
        self.assertEqual(str(self.user), 'john@example.com')

    # ── update_credentials ───────────────────────────────────────────────────

    def test_update_credentials_email(self):
        self.user.update_credentials(email='new@example.com')
        self.assertEqual(self.user.email, 'new@example.com')

    def test_update_credentials_does_not_save(self):
        """Mutation should not persist until caller calls .save()."""
        self.user.update_credentials(email='new@example.com')
        fresh = User.objects.get(id=self.user.id)
        self.assertEqual(fresh.email, 'john@example.com')  # still old in DB

    def test_update_credentials_username(self):
        self.user.update_credentials(username='johnny')
        self.assertEqual(self.user.username, 'johnny')

    def test_update_credentials_password(self):
        self.user.update_credentials(password='NewPass456!')
        self.assertTrue(self.user.check_password('NewPass456!'))

    def test_update_credentials_none_values_ignored(self):
        """Passing None should not overwrite existing values."""
        self.user.update_credentials(email=None)
        self.assertEqual(self.user.email, 'john@example.com')

    # ── mark_onboarded ────────────────────────────────────────────────────────

    def test_mark_onboarded_sets_flag(self):
        self.assertFalse(self.user.is_onboarded)
        self.user.mark_onboarded()
        self.assertTrue(self.user.is_onboarded)

    def test_mark_onboarded_does_not_save(self):
        self.user.mark_onboarded()
        fresh = User.objects.get(id=self.user.id)
        self.assertFalse(fresh.is_onboarded)  # not persisted yet

    # ── has_completed_onboarding ──────────────────────────────────────────────

    def test_has_completed_onboarding_false_by_default(self):
        self.assertFalse(self.user.has_completed_onboarding)

    def test_has_completed_onboarding_true_after_mark(self):
        self.user.mark_onboarded()
        self.assertTrue(self.user.has_completed_onboarding)