from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site

from userena.models import UserenaBaseProfile


class UserSite(models.Model):

    USER = 0
    STAFF = 1
    SUPERUSER = 2

    ROLE_TYPE = ((USER, 'Benutzer', ),
                 (STAFF, 'Redakteur', ),
                 (SUPERUSER, 'Administrator', ),
                 )
    user = models.ForeignKey('UserProfile')
    site = models.ForeignKey(Site)
    role = models.IntegerField(choices=ROLE_TYPE, default=0)


class UserProfile(UserenaBaseProfile):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                unique=True,
                                verbose_name=_('Benutzer'),
                                related_name='userprofile')
    sites = models.ManyToManyField(Site, through=UserSite, blank=True)

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)

        # register user for the "current" site if no sites are registered
        # so far
        if not self.sites.count():
            if self.user.is_superuser:
                role = UserSite.SUPERUSER
            elif self.user.is_staff:
                role = UserSite.STAFF
            else:
                role = UserSite.USER
            us = UserSite(user=self, site=Site.objects.get_current(),
                          role=role)
            us.save()


