from django.apps import AppConfig


class ChatSupportConfig(AppConfig):  # ✅ Keep the app name relevant to Ticket Support
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat_support'

    def ready(self):
        """
        Import signals to enable ticket escalations.
        """
        import chat_support.signals  # ✅ Ensure signals like ticket escalations are loaded
