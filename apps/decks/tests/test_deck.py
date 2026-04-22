from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.decks.models import Deck
from apps.languages.models import Language

User = get_user_model()


class TestDeck(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='john', email='john@example.com', password='pass'
        )
        self.other_user = User.objects.create_user(
            username='jane', email='jane@example.com', password='pass'
        )
        self.language = Language.objects.create(
            name='Spanish', code='es', flag_emoji='🇪🇸'
        )
        self.deck = Deck.objects.create(
            owner=self.user,
            language=self.language,
            title='My Deck',
        )

    # ── Factory ──────────────────────────────────────────────────────────────

    def test_create_saves_to_db(self):
        self.assertIsNotNone(self.deck.id)

    def test_create_sets_title(self):
        self.assertEqual(self.deck.title, 'My Deck')

    def test_default_is_public_false(self):
        self.assertFalse(self.deck.is_public)

    def test_default_is_generated_false(self):
        self.assertFalse(self.deck.is_generated)

    def test_str_returns_title(self):
        self.assertEqual(str(self.deck), 'My Deck')

    # ── update ───────────────────────────────────────────────────────────────

    def test_update_title(self):
        self.deck.update(title='Updated Deck')
        self.assertEqual(self.deck.title, 'Updated Deck')

    def test_update_description(self):
        self.deck.update(description='A new description')
        self.assertEqual(self.deck.description, 'A new description')

    def test_update_is_public(self):
        self.deck.update(is_public=True)
        self.assertTrue(self.deck.is_public)

    def test_update_does_not_save(self):
        self.deck.update(title='Updated')
        fresh = Deck.objects.get(id=self.deck.id)
        self.assertEqual(fresh.title, 'My Deck')   # not persisted

    def test_update_none_values_ignored(self):
        self.deck.update(title=None)
        self.assertEqual(self.deck.title, 'My Deck')

    # ── clone_for ────────────────────────────────────────────────────────────

    def test_clone_for_creates_new_deck(self):
        clone = self.deck.clone_for(self.other_user)
        self.assertIsNone(clone.id)   # not saved yet
        self.assertEqual(clone.owner, self.other_user)

    def test_clone_copies_language(self):
        clone = self.deck.clone_for(self.other_user)
        self.assertEqual(clone.language, self.language)

    def test_clone_appends_copy_to_title(self):
        clone = self.deck.clone_for(self.other_user)
        self.assertIn('copy', clone.title)

    def test_clone_is_private(self):
        self.deck.is_public = True
        clone = self.deck.clone_for(self.other_user)
        self.assertFalse(clone.is_public)   # clone always starts private

    def test_clone_does_not_save(self):
        clone = self.deck.clone_for(self.other_user)
        self.assertIsNone(clone.id)

    # ── is_owned_by ──────────────────────────────────────────────────────────

    def test_is_owned_by_owner(self):
        self.assertTrue(self.deck.is_owned_by(self.user))

    def test_is_not_owned_by_other_user(self):
        self.assertFalse(self.deck.is_owned_by(self.other_user))