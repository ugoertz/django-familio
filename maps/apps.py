from django.apps import AppConfig
from watson import search as watson


class MapsConfig(AppConfig):
    name = "maps"
    verbose_name = "Landkarten"

    def ready(self):
        PlaceModel = self.get_model("Place")
        watson.register(PlaceModel, store=('handle', ))

