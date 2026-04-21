from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    @classmethod
    def create(cls, name: str) -> 'Tag':
        return cls.objects.create(name=name)

    def __str__(self) -> str:
        return self.name