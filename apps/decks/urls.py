from django.urls import path
from apps.decks.views.deck_views import (
    DeckListView, DeckCreateView, DeckDetailView,
    DeckUpdateView, DeckDeleteView,
)
from apps.decks.views.flashcard_views import (
    FlashcardCreateView, FlashcardBulkCreateView,
    FlashcardUpdateView, FlashcardDeleteView,
)

app_name = 'decks'

urlpatterns = [
    path('',                            DeckListView.as_view(),         name='list'),
    path('new/',                        DeckCreateView.as_view(),        name='create'),
    path('<int:deck_id>/',              DeckDetailView.as_view(),        name='detail'),
    path('<int:deck_id>/edit/',         DeckUpdateView.as_view(),        name='update'),
    path('<int:deck_id>/delete/',       DeckDeleteView.as_view(),        name='delete'),
    path('<int:deck_id>/cards/add/',    FlashcardCreateView.as_view(),   name='card-create'),
    path('<int:deck_id>/cards/bulk/',   FlashcardBulkCreateView.as_view(),name='card-bulk'),
    path('cards/<int:card_id>/edit/',   FlashcardUpdateView.as_view(),   name='card-update'),
    path('cards/<int:card_id>/delete/', FlashcardDeleteView.as_view(),   name='card-delete'),
]