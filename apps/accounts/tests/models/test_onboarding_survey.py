from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import LanguageLearner, OnboardingSurvey
from apps.languages.models import Language, ProficiencyLevel

User = get_user_model()


class TestOnboardingSurvey(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john',
            email='john@example.com',
            password='pass',
        )
        self.language = Language.objects.create(
            name='Spanish', code='es', flag_emoji='🇪🇸',
        )
        self.level = ProficiencyLevel.objects.create(
            code='A1', label='Beginner',
            description='Beginner level',
            order=1, min_xp=0, max_xp=999,
        )
        self.learner = LanguageLearner.objects.create(
            user=self.user,
            language=self.language,
        )
        self.survey = OnboardingSurvey.objects.create(learner=self.learner)

    # ── Factory ──────────────────────────────────────────────────────────────

    def test_create_saves_to_db(self):
        self.assertIsNotNone(self.survey.id)

    def test_create_links_to_learner(self):
        self.assertEqual(self.survey.learner, self.learner)

    def test_is_not_completed_on_creation(self):
        self.assertFalse(self.survey.is_completed)
        self.assertIsNone(self.survey.completed_at)

    # ── complete() ───────────────────────────────────────────────────────────

    def test_complete_sets_all_fields(self):
        self.survey.complete(
            goal='travel',
            experience_level=self.level,
            hours_per_week=5,
        )
        self.assertEqual(self.survey.learning_goal, 'travel')
        self.assertEqual(self.survey.experience_level, self.level)
        self.assertEqual(self.survey.hours_per_week, 5)

    def test_complete_sets_completed_at(self):
        self.assertIsNone(self.survey.completed_at)
        self.survey.complete(
            goal='career',
            experience_level=self.level,
            hours_per_week=3,
        )
        self.assertIsNotNone(self.survey.completed_at)

    def test_complete_does_not_save(self):
        """complete() mutates only — caller must save."""
        self.survey.complete(
            goal='travel',
            experience_level=self.level,
            hours_per_week=5,
        )
        fresh = OnboardingSurvey.objects.get(id=self.survey.id)
        self.assertIsNone(fresh.completed_at)   # not persisted

    def test_complete_twice_raises(self):
        """Domain invariant — completing twice is an error."""
        self.survey.complete(
            goal='travel',
            experience_level=self.level,
            hours_per_week=5,
        )
        self.survey.save()

        with self.assertRaises(ValueError):
            self.survey.complete(
                goal='career',
                experience_level=self.level,
                hours_per_week=2,
            )

    # ── is_completed ─────────────────────────────────────────────────────────

    def test_is_completed_false_before_complete(self):
        self.assertFalse(self.survey.is_completed)

    def test_is_completed_true_after_complete(self):
        self.survey.complete(
            goal='travel',
            experience_level=self.level,
            hours_per_week=5,
        )
        self.assertTrue(self.survey.is_completed)