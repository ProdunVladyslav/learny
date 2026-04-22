import datetime
from typing import Optional, TYPE_CHECKING

from django.db import models

from shared.value_objects import DailyGoal

if TYPE_CHECKING:
    from apps.accounts.models.custom_user import CustomUser
    from apps.languages.models import Language


class UserProfile(models.Model):
    """
    Entity — part of the User Aggregate.
    Stores preferences and display settings that belong to a user
    but don't fit on the auth model itself.

    Never fetched without first having CustomUser — always accessed
    via user.profile, never UserProfile.objects.get() directly in use cases.
    """

    user = models.OneToOneField(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='profile',
    )
    native_language = models.ForeignKey(
        'languages.Language',
        on_delete=models.RESTRICT,
        null=True,
        related_name='+',
    )
    timezone           = models.CharField(max_length=50, blank=True)
    daily_goal_minutes = models.PositiveIntegerField(default=10)
    avatar             = models.URLField(blank=True, null=True)

    # ── Factory ──────────────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        user:            'CustomUser',
        native_language: 'Language',
        timezone:        str,
    ) -> 'UserProfile':
        return cls.objects.create(
            user=user,
            native_language=native_language,
            timezone=timezone,
        )

    # ── Mutations (do NOT save — caller/use case is responsible) ─────────────

    def update(
        self,
        native_language: Optional['Language'] = None,
        timezone:        Optional[str]         = None,
        daily_goal:      Optional[DailyGoal]   = None,
        avatar:          Optional[str]          = None,
    ) -> None:
        """
        Does NOT save — caller responsible.
        Accepts DailyGoal value object instead of raw int.
        Why? DailyGoal encapsulates min/max validation and
        the hours→minutes conversion in one place.
        """
        if native_language is not None:
            self.native_language = native_language
        if timezone is not None:
            self.timezone = timezone
        if daily_goal is not None:
            self.daily_goal_minutes = daily_goal.minutes
        if avatar is not None:
            self.avatar = avatar

    def set_goal_from_hours_per_week(self, hours: int) -> None:
        """
        Converts onboarding input (hours/week) to daily minutes.
        Does NOT save — caller responsible.
        """
        self.daily_goal_minutes = DailyGoal.from_hours_per_week(hours).minutes

    # ── Queries ──────────────────────────────────────────────────────────────

    @property
    def local_time(self) -> datetime.datetime:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(self.timezone) if self.timezone else datetime.timezone.utc
        return datetime.datetime.now(tz)

    @property
    def daily_goal(self) -> DailyGoal:
        """Expose stored int as a typed Value Object for domain logic."""
        return DailyGoal(self.daily_goal_minutes)

    def __str__(self) -> str:
        return str(self.user)