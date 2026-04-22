from apps.accounts.models import CustomUser, UserProfile
from shared.repositories import BaseRepository


class UserRepository(BaseRepository[CustomUser]):
    def __init__(self):
        super().__init__(CustomUser)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_email(self, email: str) -> CustomUser | None:
        return self._model.objects.filter(email=email).first()

    def get_by_username(self, username: str) -> CustomUser | None:
        return self._model.objects.filter(username=username).first()

    def get_with_profile(self, user_id: int) -> CustomUser:
        """
        Fetches user and profile in one query via select_related.
        Use when you know you'll access user.profile — avoids N+1.
        """
        return self._model.objects.select_related('profile').get(id=user_id)

    # ── Profile (part of User aggregate — lives in UserRepository) ────────────

    def save_profile(self, profile: UserProfile) -> UserProfile:
        """
        Profile is part of the User aggregate — its persistence
        belongs to UserRepository, not a separate ProfileRepository.
        """
        profile.save()
        return profile