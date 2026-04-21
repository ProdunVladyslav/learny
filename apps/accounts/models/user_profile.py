import datetime
from typing import Optional

from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='profile'
    )
    native_language = models.ForeignKey(
        'languages.Language',
        on_delete=models.RESTRICT,
        null=True,
        related_name='+'
    )
    timezone = models.CharField(max_length=50, blank=True)
    daily_goal_minutes = models.PositiveIntegerField(default=10)
    avatar = models.URLField(blank=True, null=True)

    @classmethod
    def create(cls, user: 'CustomUser', native_language: 'Language', timezone: str):
        return cls.objects.create(user=user, native_language=native_language, timezone=timezone)

    def update(
            self,
            native_language=None,
            timezone=None,
            daily_goal_minutes=None,
            avatar=None,
    ) -> None:
        """Does NOT save — caller is responsible."""
        if native_language is not None:
            self.native_language = native_language
        if timezone is not None:
            self.timezone = timezone
        if daily_goal_minutes is not None:
            self.daily_goal_minutes = daily_goal_minutes
        if avatar is not None:
            self.avatar = avatar

    @property
    def local_time(self):
        import zoneinfo
        tz = zoneinfo.ZoneInfo(self.timezone) if self.timezone else datetime.timezone.utc
        return datetime.datetime.now(tz)

    def add_hours_per_week(self, hours_per_week: int):
        self.daily_goal_minutes += round(hours_per_week * 60 / 7)

    def remove_hours_per_week(self, hours_per_week: int):
        self.daily_goal_minutes -= round(hours_per_week * 60 / 7)

    def __str__(self):
        return str(self.user)
