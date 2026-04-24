from apps.accounts.forms import SignupForm
from apps.accounts.models import LanguageLearner
from apps.accounts.repositories import UserRepository
from apps.accounts.results import SignupResult
from apps.languages.models import Language
from shared.domain_events import UserRegistered
from shared.event_bus import EventBus


class SignupUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, form: SignupForm) -> SignupResult:
        try:
            user = form.save(commit=False)
            self.user_repo.save(user)

            default_language = Language.objects.first()
            if default_language:
                LanguageLearner.objects.get_or_create(
                    user=user,
                    language_to=default_language,
                )

            EventBus.publish(UserRegistered(
                user_id=user.id,
                email=user.email,
                username=user.username,
            ))

            return SignupResult(success=True, user=user)

        except Exception as e:
            return SignupResult(success=False, error=str(e))