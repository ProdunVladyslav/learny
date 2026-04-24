from django.apps import AppConfig


class LanguagesConfig(AppConfig):
    name = 'apps.languages'

    def ready(self):
        from django.db import connection
        try:
            # only run if the table actually exists (i.e. migrations have run)
            if 'languages_language' in connection.introspection.table_names():
                from apps.languages.management.commands.seed_languages import Command
                Command().handle()
        except Exception:
            pass  # never crash the server on seed failure