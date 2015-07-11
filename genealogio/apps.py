from django.apps import AppConfig
import watson


class GenealogioConfig(AppConfig):
    name = "genealogio"
    verbose_name = "Familiengeschichte"

    def ready(self):
        PersonModel = self.get_model("Person")
        watson.register(PersonModel.objects.all(),
                        fields=('first_name', 'last_name', 'last_name_current',
                                'name_set__name', 'places', 'handle',
                                'datebirth', 'datedeath',
                                'events', 'comments'),
                        store=('get_primary_name', 'handle', ))

        FamilyModel = self.get_model("Family")
        watson.register(FamilyModel.objects.all(), store=('handle', 'name', ))

        EventModel = self.get_model("Event")
        watson.register(EventModel.objects.all(), store=('handle', ))

        TimelineItemModel = self.get_model("TimelineItem")
        watson.register(TimelineItemModel.objects.all())

