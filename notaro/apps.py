from django.apps import AppConfig
import watson


class NotaroConfig(AppConfig):
    name = "notaro"
    verbose_name = "Notizen"

    def ready(self):
        NoteModel = self.get_model("Note")
        watson.register(NoteModel.objects.filter(published=True))

        SourceModel = self.get_model("Source")
        watson.register(SourceModel.objects.all())

        DocumentModel = self.get_model("Document")
        watson.register(DocumentModel.objects.all(), exclude=('doc'))
