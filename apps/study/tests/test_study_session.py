from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import LanguageLearner
from apps.decks.models import Deck
from apps.languages.models import Language
from apps.study.models import StudySession

User = get_user_model()


class TestStudySession(TestCase):

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
        self.session = StudySession.objects.create(
            user=self.learner,
            deck=self.deck,
            mode='spaced',
            cards_target=10,
            started_at=__import__('django.utils.timezone', fromlist=['timezone']).timezone.now(),
        )

    # ── Factory ──────────────────────────────────────────────────────────────

    def test_create_saves_to_db(self):
        self.assertIsNotNone(self.session.id)

    def test_create_sets_started_at(self):
        self.assertIsNotNone(self.session.started_at)

    def test_not_finished_on_creation(self):
        self.assertFalse(self.session.is_finished)
        self.assertIsNone(self.session.ended_at)

    # ── close ────────────────────────────────────────────────────────────────

    def test_close_sets_ended_at(self):
        self.session.close()
        self.assertIsNotNone(self.session.ended_at)

    def test_close_marks_as_finished(self):
        self.session.close()
        self.assertTrue(self.session.is_finished)

    def test_close_does_not_save(self):
        self.session.close()
        fresh = StudySession.objects.get(id=self.session.id)
        self.assertIsNone(fresh.ended_at)   # not persisted

    def test_close_twice_raises(self):
        """Domain invariant — closing twice corrupts duration."""
        self.session.close()
        with self.assertRaises(ValueError):
            self.session.close()

    # ── duration_seconds ─────────────────────────────────────────────────────

    def test_duration_none_when_not_closed(self):
        self.assertIsNone(self.session.duration_seconds)

    def test_duration_positive_after_close(self):
        self.session.close()
        self.assertIsNotNone(self.session.duration_seconds)
        self.assertGreaterEqual(self.session.duration_seconds, 0)

    # ── has_reached_target ────────────────────────────────────────────────────

    def test_has_not_reached_target_initially(self):
        self.assertFalse(self.session.has_reached_target())

    def test_no_target_never_reaches(self):
        self.session.cards_target = None
        self.assertFalse(self.session.has_reached_target())