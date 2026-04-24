# apps/languages/management/commands/seed_languages.py

from django.core.management.base import BaseCommand
from apps.languages.models import Language, ProficiencyLevel


LANGUAGES = [
    {'name': 'English',    'code': 'en', 'flag_emoji': '🇬🇧'},
    {'name': 'Ukrainian',  'code': 'uk', 'flag_emoji': '🇺🇦'},
    {'name': 'Spanish',    'code': 'es', 'flag_emoji': '🇪🇸'},
    {'name': 'French',     'code': 'fr', 'flag_emoji': '🇫🇷'},
    {'name': 'German',     'code': 'de', 'flag_emoji': '🇩🇪'},
    {'name': 'Italian',    'code': 'it', 'flag_emoji': '🇮🇹'},
    {'name': 'Portuguese', 'code': 'pt', 'flag_emoji': '🇵🇹'},
    {'name': 'Polish',     'code': 'pl', 'flag_emoji': '🇵🇱'},
    {'name': 'Japanese',   'code': 'ja', 'flag_emoji': '🇯🇵'},
    {'name': 'Korean',     'code': 'ko', 'flag_emoji': '🇰🇷'},
    {'name': 'Chinese',    'code': 'zh', 'flag_emoji': '🇨🇳'},
    {'name': 'Arabic',     'code': 'ar', 'flag_emoji': '🇸🇦'},
]

PROFICIENCY_LEVELS = [
    {
        'code': 'A1', 'label': 'Beginner',
        'description': 'Can understand and use basic phrases.',
        'order': 1, 'min_xp': 0, 'max_xp': 499,
    },
    {
        'code': 'A2', 'label': 'Elementary',
        'description': 'Can communicate in simple and routine tasks.',
        'order': 2, 'min_xp': 500, 'max_xp': 1499,
    },
    {
        'code': 'B1', 'label': 'Intermediate',
        'description': 'Can deal with most situations while travelling.',
        'order': 3, 'min_xp': 1500, 'max_xp': 3499,
    },
    {
        'code': 'B2', 'label': 'Upper Intermediate',
        'description': 'Can interact with a degree of fluency.',
        'order': 4, 'min_xp': 3500, 'max_xp': 6999,
    },
    {
        'code': 'C1', 'label': 'Advanced',
        'description': 'Can express ideas fluently and spontaneously.',
        'order': 5, 'min_xp': 7000, 'max_xp': 14999,
    },
    {
        'code': 'C2', 'label': 'Mastery',
        'description': 'Can understand virtually everything heard or read.',
        'order': 6, 'min_xp': 15000, 'max_xp': 999999,
    },
]


class Command(BaseCommand):
    help = 'Seed languages and proficiency levels'

    def handle(self, *args, **options):
        self._seed_proficiency_levels()
        self._seed_languages()

    def _seed_proficiency_levels(self):
        created = 0
        for data in PROFICIENCY_LEVELS:
            _, was_created = ProficiencyLevel.objects.update_or_create(
                code=data['code'],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f'Proficiency levels: {created} created, {len(PROFICIENCY_LEVELS) - created} already existed'
        ))

    def _seed_languages(self):
        created = 0
        for data in LANGUAGES:
            _, was_created = Language.objects.update_or_create(
                code=data['code'],
                defaults=data,
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f'Languages: {created} created, {len(LANGUAGES) - created} already existed'
        ))