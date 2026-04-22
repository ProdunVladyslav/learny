from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import LanguageLearner
from apps.decks.models import Deck, Flashcard
from apps.languages.models import Language
from apps.study.constants import CARD_XP_CAP
from apps.study.models import CardProgress, CardXPRecord

User = get_user_model()


class TestCardXPRecord(TestCase):

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
        self.xp_record = CardXPRecord.objects.create(progress=self.progress)

    # ── Defaults ─────────────────────────────────────────────────────────────

    def test_default_total_xp_is_zero(self):
        self.assertEqual(self.xp_record.total_xp_earned, 0)

    def test_default_last_studied_is_none(self):
        self.assertIsNone(self.xp_record.last_studied_at)

    # ── Convenience accessors ─────────────────────────────────────────────────

    def test_learner_property_returns_language_learner(self):
        self.assertEqual(self.xp_record.learner, self.learner)

    def test_card_property_returns_flashcard(self):
        self.assertEqual(self.xp_record.card, self.flashcard)

    # ── remaining_xp_capacity ────────────────────────────────────────────────

    def test_full_capacity_when_no_xp_earned(self):
        self.assertEqual(self.xp_record.remaining_xp_capacity(), CARD_XP_CAP)

    def test_capacity_decreases_as_xp_earned(self):
        self.xp_record.total_xp_earned = 50
        self.assertEqual(self.xp_record.remaining_xp_capacity(), CARD_XP_CAP - 50)

    def test_capacity_is_zero_when_capped(self):
        self.xp_record.total_xp_earned = CARD_XP_CAP
        self.assertEqual(self.xp_record.remaining_xp_capacity(), 0)

    def test_capacity_never_negative(self):
        self.xp_record.total_xp_earned = CARD_XP_CAP + 100
        self.assertEqual(self.xp_record.remaining_xp_capacity(), 0)

    # ── is_capped ────────────────────────────────────────────────────────────

    def test_not_capped_by_default(self):
        self.assertFalse(self.xp_record.is_capped())

    def test_capped_when_at_limit(self):
        self.xp_record.total_xp_earned = CARD_XP_CAP
        self.assertTrue(self.xp_record.is_capped())

    def test_capped_when_over_limit(self):
        self.xp_record.total_xp_earned = CARD_XP_CAP + 1
        self.assertTrue(self.xp_record.is_capped())

    # ── add_xp ───────────────────────────────────────────────────────────────

    def test_add_xp_returns_awarded_amount(self):
        awarded = self.xp_record.add_xp(10)
        self.assertEqual(awarded, 10)

    def test_add_xp_updates_total(self):
        self.xp_record.add_xp(10)
        self.assertEqual(self.xp_record.total_xp_earned, 10)

    def test_add_xp_sets_last_studied_at(self):
        self.assertIsNone(self.xp_record.last_studied_at)
        self.xp_record.add_xp(10)
        self.assertIsNotNone(self.xp_record.last_studied_at)

    def test_add_xp_respects_cap(self):
        """If near cap, only awards what's left."""
        self.xp_record.total_xp_earned = CARD_XP_CAP - 5
        awarded = self.xp_record.add_xp(20)
        self.assertEqual(awarded, 5)
        self.assertEqual(self.xp_record.total_xp_earned, CARD_XP_CAP)

    def test_add_xp_awards_zero_when_capped(self):
        self.xp_record.total_xp_earned = CARD_XP_CAP
        awarded = self.xp_record.add_xp(50)
        self.assertEqual(awarded, 0)
        self.assertEqual(self.xp_record.total_xp_earned, CARD_XP_CAP)

    def test_add_xp_does_not_save(self):
        """Mutation only — caller must save."""
        self.xp_record.add_xp(10)
        fresh = CardXPRecord.objects.get(id=self.xp_record.id)
        self.assertEqual(fresh.total_xp_earned, 0)   # not persisted

    # ── is_cap_expired ───────────────────────────────────────────────────────

    def test_cap_expired_returns_none_when_never_studied(self):
        self.assertIsNone(self.xp_record.is_cap_expired())

    def test_cap_not_expired_when_recently_studied(self):
        self.xp_record.last_studied_at = timezone.now()
        self.assertFalse(self.xp_record.is_cap_expired(reset_after_days=30))

    def test_cap_expired_after_reset_period(self):
        from datetime import timedelta
        self.xp_record.last_studied_at = timezone.now() - timedelta(days=31)
        self.assertTrue(self.xp_record.is_cap_expired(reset_after_days=30))

    # ── reset_cap ────────────────────────────────────────────────────────────

    def test_reset_cap_clears_xp_and_timestamp(self):
        self.xp_record.total_xp_earned = CARD_XP_CAP
        self.xp_record.last_studied_at = timezone.now()
        self.xp_record.reset_cap()
        self.assertEqual(self.xp_record.total_xp_earned, 0)
        self.assertIsNone(self.xp_record.last_studied_at)

    def test_reset_cap_does_not_save(self):
        self.xp_record.total_xp_earned = CARD_XP_CAP
        self.xp_record.save()
        self.xp_record.reset_cap()
        fresh = CardXPRecord.objects.get(id=self.xp_record.id)
        self.assertEqual(fresh.total_xp_earned, CARD_XP_CAP)  # not persisted