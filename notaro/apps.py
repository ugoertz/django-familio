from django.apps import AppConfig
from watson import search as watson


class NotaroConfig(AppConfig):
    name = "notaro"
    verbose_name = "Notizen"

    def ready(self):
        NoteModel = self.get_model("Note")
        watson.register(NoteModel.objects.filter(published=True))

        SourceModel = self.get_model("Source")
        watson.register(SourceModel.objects.all())

        DocumentModel = self.get_model("Document")
        watson.register(DocumentModel.objects.all(), exclude=('doc', 'image'))

        PictureModel = self.get_model("Picture")
        watson.register(PictureModel.objects.all(), exclude=('image'))

        VideoModel = self.get_model("Video")
        watson.register(VideoModel.objects.all(), exclude=('video', 'poster'))
