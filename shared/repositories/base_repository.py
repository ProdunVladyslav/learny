"""
BaseRepository — generic CRUD every concrete repository inherits.

Why Generic?
  Without this, every repo repeats get_by_id(), save(), delete() identically.
  Generic base writes it once. Concrete repos only add domain-specific queries.

How it works:
  BaseRepository[T] is parameterized by the model type.
  Concrete repo passes its model class to super().__init__(model).
  All base methods then operate on that model transparently.

Usage:
    class UserRepository(BaseRepository[CustomUser]):
        def __init__(self):
            super().__init__(CustomUser)

        # only add domain-specific queries here
        def get_by_email(self, email: str) -> CustomUser | None: ...
"""
from typing import Generic, TypeVar, Type

from django.db import models
from django.db.models import QuerySet

T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self._model = model

    # ── Read ─────────────────────────────────────────────────────────────────

    def get_by_id(self, id: int) -> T:
        """
        Raises DoesNotExist if not found.
        Use case catches this and returns appropriate result.
        """
        return self._model.objects.get(id=id)

    def get_by_id_or_none(self, id: int) -> T | None:
        return self._model.objects.filter(id=id).first()

    def get_all(self) -> QuerySet[T]:
        return self._model.objects.all()

    def exists(self, **kwargs) -> bool:
        return self._model.objects.filter(**kwargs).exists()

    def filter(self, **kwargs) -> QuerySet[T]:
        return self._model.objects.filter(**kwargs)

    # ── Write ─────────────────────────────────────────────────────────────────

    def save(self, instance: T) -> T:
        instance.save()
        return instance

    def save_fields(self, instance: T, fields: list[str]) -> T:
        """
        Optimized save — only updates specified columns.
        Use when you know exactly what changed (e.g. is_active toggle).
        Avoids overwriting concurrent changes to other fields.
        """
        instance.save(update_fields=fields)
        return instance

    def delete(self, instance: T) -> None:
        instance.delete()

    def bulk_create(self, instances: list[T]) -> list[T]:
        return self._model.objects.bulk_create(instances)

    def bulk_update(self, instances: list[T], fields: list[str]) -> None:
        self._model.objects.bulk_update(instances, fields)