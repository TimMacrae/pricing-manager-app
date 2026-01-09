from django.apps import AppConfig


class TestingConfig(AppConfig):
    name = 'testing'

    def ready(self):
        from . import signals  # noqa
