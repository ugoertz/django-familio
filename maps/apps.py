from django.apps import AppConfig
import watson


class MapsConfig(AppConfig):
    name = "maps"
    verbose_name = "Landkarten"

    def ready(self):
        PlaceModel = self.get_model("Place")
        watson.register(PlaceModel, store=('handle', ))

