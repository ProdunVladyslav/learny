from collections import defaultdict

from apps.accounts.repositories import LanguageLearnerRepository
from apps.study.forms import GetDailyReviewForm
from apps.study.repositories import CardProgressRepository
from apps.study.results import DailyReviewSummaryResult, DueCardDto


class GetDailyReviewUseCase:
    def __init__(self, progress_repo: CardProgressRepository, learner_repo: LanguageLearnerRepository):
        self.progress_repo = progress_repo
        self.learner_repo = learner_repo

    def execute(self, user, form: GetDailyReviewForm) -> DailyReviewSummaryResult:
        if not form.is_valid():
            return DailyReviewSummaryResult(success=False, error=form.errors)

        deck_id = form.cleaned_data.get('deck_id')

        learner = self.learner_repo.get_active_for_user(user)
        if learner is None:
            return DailyReviewSummaryResult(success=True, due_count=0, new_count=0, total=0)

        due_qs, new_qs = self.progress_repo.get_due_and_new_for_today(
            learner=learner,
            deck_id=deck_id,
        )

        due_progresses = list(due_qs)
        new_progresses = list(new_qs)

        all_progresses = due_progresses + new_progresses

        if not all_progresses:
            return DailyReviewSummaryResult(
                success=True,
                due_count=0,
                new_count=0,
                total=0,
            )

        due_cards = [DueCardDto.from_progress(p) for p in all_progresses]

        # group by deck for the summary panel
        by_deck = {}
        for p in all_progresses:
            deck_id = p.flashcard.deck_id
            if deck_id not in by_deck:
                by_deck[deck_id] = {'title': p.flashcard.deck.title, 'count': 0}
            by_deck[deck_id]['count'] += 1

        return DailyReviewSummaryResult(
            success=True,
            due_count=len(due_progresses),
            new_count=len(new_progresses),
            total=len(all_progresses),
            due_cards=due_cards,
            by_deck=dict(by_deck),
        )