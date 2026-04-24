from django.urls import path
from apps.study.views.review_views import DailyReviewView, SubmitAnswerView
from apps.study.views.session_views import StartSessionView, CloseSessionView

app_name = 'study'

urlpatterns = [
    path('review/',          DailyReviewView.as_view(),  name='review'),
    path('answer/',          SubmitAnswerView.as_view(),  name='submit-answer'),
    path('session/start/',   StartSessionView.as_view(),  name='session-start'),
    path('session/close/',   CloseSessionView.as_view(),  name='session-close'),
]