from typing import Optional

from django.db import models


class Flashcard(models.Model):
    deck = models.ForeignKey(
        'Deck',
        on_delete=models.CASCADE,
        related_name='flashcards')
    front = models.CharField(max_length=200)
    back = models.CharField(max_length=200)
    hint = models.TextField(blank=True)
    audio_url = models.URLField(max_length=200, blank=True)
    image_url = models.URLField(max_length=200, blank=True)
    tags = models.ManyToManyField(
        'Tag',
        related_name='flashcards'  # tag.flashcards.all() — clearer
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, deck, front, back):
        return cls.objects.create(
            deck=deck,
            front=front,
            back=back,
        )

    def update(
            self,
            front: Optional[str] = None,
            back: Optional[str] = None,
            hint: Optional[str] = None,
            audio_url: Optional[str] = None,
            image_url: Optional[str] = None,
    ) -> None:
        if front is not None:
            self.front = front
        if back is not None:
            self.back = back
        if hint is not None:
            self.hint = hint
        if audio_url is not None:
            self.audio_url = audio_url
        if image_url is not None:
            self.image_url = image_url

    def set_tags(self, tag_list: list) -> None:
        self.tags.set(tag_list)

    @property
    def has_hint(self) -> bool:
        return bool(self.hint)

    def __str__(self) -> str:
        return f"{self.front} → {self.back}"