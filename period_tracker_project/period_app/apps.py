from django.apps import AppConfig

class PeriodAppConfig(AppConfig):
    name = 'period_app'

    def ready(self):
        import period_app.signals
