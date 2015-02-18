from django.apps import AppConfig
import watson


class NotaroConfig(AppConfig):
    name = "notaro"
    verbose_name = "Notizen"

    def ready(self):
        NoteModel = self.get_model("Note")
        watson.register(NoteModel.objects.filter(published=True))
