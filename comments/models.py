from django.db import models
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from dbarray import IntegerArrayField


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField(verbose_name="Dein Kommentar")
    date = models.DateTimeField(auto_now_add=True)
    path = IntegerArrayField(blank=True, editable=False, unique=True)

    # Content-object field
    content_type = models.ForeignKey(
                       ContentType,
                       verbose_name=_('content type'),
                       related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(
                         ct_field="content_type",
                         fk_field="object_pk")

    site = models.ForeignKey(Site)

    def depth(self):
        return 30 * (len(self.path) - 1)

    def __unicode__(self):
        return self.content

    class Meta:
        ordering = ('path', )

