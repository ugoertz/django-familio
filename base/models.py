from django.db import models
from django.contrib.sites.models import Site


class SiteProfile(models.Model):

    site = models.OneToOneField(Site, on_delete=models.CASCADE)

    # Person, Family and Event objects created on the current site will by
    # default be added to the following sites as well:
    neighbor_sites = models.ManyToManyField(Site, blank=True,
                                            related_name="neighbors")

    short_name = models.CharField(max_length=50)

    def __str__(self):
        return '%s (%s)' % (self.short_name, self.site.domain)

    class Meta:
        verbose_name = "FBaumProfil"
        verbose_name_plural = "FBaumProfile"

