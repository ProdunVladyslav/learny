from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from apps.study.container import StudyContainer
from apps.study.forms import GetDailyReviewForm, SubmitAnswerForm


class DailyReviewView(LoginRequiredMixin, View):
    def get(self, request):
        form = GetDailyReviewForm(request.GET)
        result = StudyContainer.get_daily_review().execute(request.user, form)
        return render(request, 'study/review.html', {'review': result})


class SubmitAnswerView(LoginRequiredMixin, View):
    def post(self, request):
        form = SubmitAnswerForm(request.POST)
        result = StudyContainer.submit_answer().execute(request.user, form)
        if not result.success:
            return JsonResponse({'success': False, 'error': str(result.error)}, status=400)
        return JsonResponse({
            'success': True,
            'xp_awarded': result.xp_awarded,
            'is_correct': result.is_correct,
            'card_mastered': result.card_mastered,
        })
