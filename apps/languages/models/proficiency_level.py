from django.db import models


class ProficiencyLevel(models.Model):
    code = models.CharField(max_length=10, unique=True)
    label = models.CharField(max_length=20, unique=True)
    description = models.TextField()
    order = models.PositiveIntegerField()
    min_xp = models.PositiveIntegerField(default=0)   # ← add
    max_xp = models.PositiveIntegerField(default=0)   # ← add

    @classmethod
    def get_for_xp(cls, xp: int) -> 'ProficiencyLevel | None':
        return cls.objects.filter(
            min_xp__lte=xp,
            max_xp__gte=xp,
        ).first()