from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from apps.study.container import StudyContainer
from apps.study.forms import StartStudySessionForm, CloseStudySessionForm
from apps.study.repositories import StudySessionRepository, CardProgressRepository
from apps.decks.repositories import DeckRepository
from apps.study.use_cases.sessions.start_study_session_use_case import StartStudySessionUseCase
from apps.study.use_cases.sessions.close_study_session_use_case import CloseStudySessionUseCase


class StartSessionView(LoginRequiredMixin, View):
    def post(self, request):
        form = StartStudySessionForm(request.POST)
        result = StudyContainer.start_session().execute(request.user, form)

        if not result.success:
            print(f'[start_session] FAILED — form_valid={form.is_valid()} form_errors={form.errors} error={result.error!r}')
            return redirect('study:review')

        return render(request, 'study/session.html', {
            'session_id': result.session_id,
            'learner_id': result.learner_id,
            'cards':      result.cards,
            'mode':       form.cleaned_data.get('mode', 'standard'),
        })


class CloseSessionView(LoginRequiredMixin, View):
    def post(self, request):
        form = CloseStudySessionForm(request.POST)
        StudyContainer.close_session().execute(request.user, form)
        return redirect('study:review')