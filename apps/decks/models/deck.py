from django.db import models

from apps.accounts.models import CustomUser
from config import settings


class Deck(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='decks'
    )
    owner_id: int
    language = models.ForeignKey(
        'languages.Language',
        on_delete=models.PROTECT,
        related_name='+'
    )
    title = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    flashcards: 'QuerySet[Flashcard]'

    @classmethod
    def create(cls, owner, language, title: str) -> 'Deck':
        return cls.objects.create(
            owner=owner,
            language=language,
            title=title,
        )

    def update(self, title=None, description=None, is_public=None) -> None:
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if is_public is not None:
            self.is_public = is_public

    def clone_for(self, user: CustomUser) -> 'Deck':
        """
        Creates a copy of this deck for another user.
        Does NOT save — caller is responsible.
        """
        return Deck(
            owner=user,
            language=self.language,
            title=f'{self.title} (copy)',
            description=self.description,
            is_public=False,  # clone starts private
            is_generated=False,
        )

    def get_card_count(self) -> int:
        return self.flashcards.count()

    def is_owned_by(self, user) -> bool:
        return self.owner_id == user.id

    def __str__(self) -> str:
        return self.title