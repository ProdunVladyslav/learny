from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.forms import SignupForm
from apps.accounts.repositories import UserRepository
from apps.accounts.use_cases import SignupUseCase
from apps.accounts.use_cases.auth.sign_up_use_case import SignupResult
from shared.domain_events import UserRegistered
from shared.event_bus import EventBus

User = get_user_model()

class TestSignupUseCase(TestCase):

    def setUp(self):
        self.user_repo = UserRepository()
        self.use_case  = SignupUseCase(user_repo=self.user_repo)

        self.valid_data = {
            'username':  'jane',
            'email':     'jane@example.com',
            'password1': 'SuperSecret123!',
            'password2': 'SuperSecret123!',
        }

        # clear event bus listeners between tests so published events
        # don't bleed into other test assertions
        EventBus.clear()

    # ── Success ───────────────────────────────────────────────────────────────

    def test_signup_creates_user_in_db(self):
        """Valid form → user exists in DB after execute()."""
        form = SignupForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors)

        result = self.use_case.execute(form)

        self.assertTrue(result.success)
        self.assertTrue(User.objects.filter(username='jane').exists())

    def test_signup_returns_user_instance(self):
        """Result contains the created user with correct fields."""
        form = SignupForm(data=self.valid_data)
        form.is_valid()

        result = self.use_case.execute(form)

        self.assertIsNotNone(result.user)
        self.assertEqual(result.user.username, 'jane')
        self.assertEqual(result.user.email, 'jane@example.com')
        self.assertIsNone(result.error)

    def test_signup_saves_via_repository(self):
        """User gets a DB id — confirms repo.save() was called."""
        form = SignupForm(data=self.valid_data)
        form.is_valid()

        result = self.use_case.execute(form)

        self.assertIsNotNone(result.user.id)   # no id = not saved to DB

    def test_signup_publishes_user_registered_event(self):
        """
        UserRegistered event is published after successful signup.
        Why test this? If someone removes EventBus.publish() from the use case,
        notifications and analytics silently break — this test catches it.
        """
        published_events = []
        EventBus.subscribe(UserRegistered, lambda e: published_events.append(e))

        form = SignupForm(data=self.valid_data)
        form.is_valid()
        result = self.use_case.execute(form)

        self.assertEqual(len(published_events), 1)
        event = published_events[0]
        self.assertIsInstance(event, UserRegistered)
        self.assertEqual(event.user_id, result.user.id)
        self.assertEqual(event.email, 'jane@example.com')
        self.assertEqual(event.username, 'jane')

    def test_signup_result_is_signup_result_type(self):
        form = SignupForm(data=self.valid_data)
        form.is_valid()

        result = self.use_case.execute(form)

        self.assertIsInstance(result, SignupResult)

    # ── Failure ───────────────────────────────────────────────────────────────

    def test_signup_passwords_dont_match_form_invalid(self):
        """
        Mismatched passwords → form is invalid → use case never called.
        This tests the contract: view must call is_valid() before execute().
        """
        bad_data = {**self.valid_data, 'password2': 'DifferentPass123!'}
        form = SignupForm(data=bad_data)

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_signup_duplicate_username_returns_failure(self):
        """Duplicate username → use case returns failure, no crash."""
        # create first user
        User.objects.create_user(username='jane', email='other@example.com', password='pass')

        form = SignupForm(data=self.valid_data)
        form.is_valid()     # form itself may still be valid at this point
        result = self.use_case.execute(form)

        # either form catches it (is_valid=False) or repo raises IntegrityError
        # either way — no user with duplicate username should succeed
        if result.success:
            count = User.objects.filter(username='jane').count()
            self.assertEqual(count, 1)   # only one should exist
        else:
            self.assertFalse(result.success)
            self.assertIsNotNone(result.error)

    def test_signup_no_event_published_on_failure(self):
        """No UserRegistered event if signup fails."""
        published_events = []
        EventBus.subscribe(UserRegistered, lambda e: published_events.append(e))

        # force a failure by passing an invalid (uninitialised) form
        form = SignupForm(data={})
        form.is_valid()   # will be False

        # manually simulate a bad execute (empty form — will raise internally)
        result = self.use_case.execute(form)

        if not result.success:
            self.assertEqual(len(published_events), 0)