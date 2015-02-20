from django.apps import AppConfig
import watson


class GenealogioConfig(AppConfig):
    name = "genealogio"
    verbose_name = "Familiengeschichte"

    def ready(self):
        PersonModel = self.get_model("Person")
        watson.register(PersonModel,
                        fields=('first_name', 'last_name',
                                'name_set__name', 'places', 'handle',
                                'datebirth', 'datedeath',
                                'events', 'comments'),
                        store=('get_primary_name', 'handle', ))

        FamilyModel = self.get_model("Family")
        watson.register(FamilyModel, store=('handle', 'name', ))

        EventModel = self.get_model("Event")
        watson.register(EventModel, store=('handle', ))

        PlaceModel = self.get_model("Place")
        watson.register(PlaceModel, store=('handle', ))

