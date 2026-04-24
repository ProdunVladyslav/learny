from typing import Optional

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
    language_from = models.ForeignKey(
        'languages.Language',
        on_delete=models.PROTECT,
        related_name='+',
        null=True, blank=True,
    )
    language_to = models.ForeignKey(
        'languages.Language',
        on_delete=models.PROTECT,
        related_name='+',
    )
    title = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    is_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    flashcards: 'QuerySet[Flashcard]'

    @classmethod
    def create(cls, owner, language_to, title: str, language_from=None) -> 'Deck':
        return cls.objects.create(
            owner=owner,
            language_to=language_to,
            language_from=language_from,
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
        return Deck(
            owner=user,
            language_to=self.language_to,
            language_from=self.language_from,
            title=f'{self.title} (copy)',
            description=self.description,
            is_public=False,
            is_generated=False,
        )

    def get_card_count(self) -> int:
        return self.flashcards.count()

    def is_owned_by(self, user) -> bool:
        return self.owner_id == user.id

    @property
    def language_to_code(self) -> str:
        return self.language_to.code

    @property
    def language_from_code(self) -> Optional[str]:
        if self.language_from_id is None:
            return None
        return self.language_from.code

    def __str__(self) -> str:
        return self.title