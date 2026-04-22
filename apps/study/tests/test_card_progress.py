from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import LanguageLearner
from apps.decks.models import Deck, Flashcard
from apps.languages.models import Language
from apps.study.models import CardProgress

User = get_user_model()


class TestCardProgress(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john', email='john@example.com', password='pass'
        )
        self.language = Language.objects.create(
            name='Spanish', code='es', flag_emoji='🇪🇸'
        )
        self.learner = LanguageLearner.objects.create(
            user=self.user, language=self.language
        )
        self.deck = Deck.objects.create(
            owner=self.user, language=self.language, title='Test Deck'
        )
        self.flashcard = Flashcard.objects.create(
            deck=self.deck, front='Hello', back='Hola'
        )
        self.progress = CardProgress.objects.create(
            user=self.learner, flashcard=self.flashcard
        )

    # ── Defaults ─────────────────────────────────────────────────────────────

    def test_default_values(self):
        self.assertEqual(self.progress.repetitions, 0)
        self.assertAlmostEqual(self.progress.ease_factor, 2.5)
        self.assertEqual(self.progress.interval_days, 0)
        self.assertIsNone(self.progress.next_review)
        self.assertIsNone(self.progress.last_seen_at)

    # ── apply_spaced ─────────────────────────────────────────────────────────

    def test_apply_spaced_sets_all_fields(self):
        review_date = date.today() + timedelta(days=6)
        self.progress.apply_spaced(
            repetitions=1,
            ease_factor=2.6,
            interval_days=6,
            next_review=review_date,
        )
        self.assertEqual(self.progress.repetitions, 1)
        self.assertAlmostEqual(self.progress.ease_factor, 2.6)
        self.assertEqual(self.progress.interval_days, 6)
        self.assertEqual(self.progress.next_review, review_date)
        self.assertIsNotNone(self.progress.last_seen_at)

    def test_apply_spaced_floors_ease_factor(self):
        """ease_factor can never go below 1.3 — SM-2 invariant."""
        self.progress.apply_spaced(
            repetitions=0,
            ease_factor=0.5,   # below minimum
            interval_days=1,
            next_review=date.today(),
        )
        self.assertAlmostEqual(self.progress.ease_factor, 1.3)

    def test_apply_spaced_does_not_save(self):
        self.progress.apply_spaced(
            repetitions=1, ease_factor=2.6,
            interval_days=6, next_review=date.today(),
        )
        fresh = CardProgress.objects.get(id=self.progress.id)
        self.assertEqual(fresh.repetitions, 0)   # not persisted

    # ── apply_cram ───────────────────────────────────────────────────────────

    def test_apply_cram_updates_ease_and_last_seen(self):
        self.progress.apply_cram(ease_factor=2.3)
        self.assertAlmostEqual(self.progress.ease_factor, 2.3)
        self.assertIsNotNone(self.progress.last_seen_at)

    def test_apply_cram_floors_ease_factor(self):
        self.progress.apply_cram(ease_factor=0.8)
        self.assertAlmostEqual(self.progress.ease_factor, 1.3)

    # ── reset ────────────────────────────────────────────────────────────────

    def test_reset_restores_defaults(self):
        self.progress.apply_spaced(
            repetitions=5, ease_factor=3.0,
            interval_days=20, next_review=date.today(),
        )
        self.progress.reset()
        self.assertEqual(self.progress.repetitions, 0)
        self.assertAlmostEqual(self.progress.ease_factor, 2.5)
        self.assertEqual(self.progress.interval_days, 0)
        self.assertIsNone(self.progress.next_review)
        self.assertIsNone(self.progress.last_seen_at)

    # ── is_new ───────────────────────────────────────────────────────────────

    def test_is_new_true_when_never_seen(self):
        self.assertTrue(self.progress.is_new)

    def test_is_new_false_after_apply_spaced(self):
        self.progress.apply_spaced(1, 2.5, 1, date.today())
        self.assertFalse(self.progress.is_new)

    # ── is_due ───────────────────────────────────────────────────────────────

    def test_is_due_true_when_no_review_date(self):
        self.assertIsNone(self.progress.next_review)
        self.assertTrue(self.progress.is_due)

    def test_is_due_true_when_review_in_past(self):
        self.progress.next_review = date.today() - timedelta(days=1)
        self.assertTrue(self.progress.is_due)

    def test_is_due_true_when_review_is_today(self):
        self.progress.next_review = date.today()
        self.assertTrue(self.progress.is_due)

    def test_is_due_false_when_review_in_future(self):
        self.progress.next_review = date.today() + timedelta(days=1)
        self.assertFalse(self.progress.is_due)

    # ── is_mastered ───────────────────────────────────────────────────────────

    def test_is_mastered_false_by_default(self):
        self.assertFalse(self.progress.is_mastered)

    def test_is_mastered_true_when_conditions_met(self):
        self.progress.repetitions = 5
        self.progress.ease_factor = 2.7
        self.assertTrue(self.progress.is_mastered)

    def test_is_mastered_false_low_repetitions(self):
        self.progress.repetitions = 4
        self.progress.ease_factor = 3.0
        self.assertFalse(self.progress.is_mastered)

    def test_is_mastered_false_low_ease(self):
        self.progress.repetitions = 5
        self.progress.ease_factor = 2.6
        self.assertFalse(self.progress.is_mastered)

    # ── strength ─────────────────────────────────────────────────────────────

    def test_strength_zero_for_new_card(self):
        self.assertEqual(self.progress.strength, 0)

    def test_strength_increases_with_repetitions(self):
        self.progress.repetitions = 5
        self.progress.ease_factor = 2.5
        self.assertGreater(self.progress.strength, 0)

    def test_strength_max_100(self):
        self.progress.repetitions = 10
        self.progress.ease_factor = 4.0
        self.assertLessEqual(self.progress.strength, 100)

    def test_strength_is_int(self):
        self.assertIsInstance(self.progress.strength, int)