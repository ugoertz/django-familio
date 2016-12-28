# -*- coding: utf8 -*-

from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from pybb.profiles import PybbProfile

from userena.models import UserenaBaseProfile
from genealogio.models import Person


class UserSite(models.Model):

    USER = 0
    STAFF = 1
    SUPERUSER = 2

    ROLE_TYPE = ((USER, 'Benutzer', ),
                 (STAFF, 'Redakteur', ),
                 (SUPERUSER, 'Administrator', ),
                 )
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_TYPE, default=0)


class UserProfile(UserenaBaseProfile, PybbProfile):
    KEYMAP_CHOICES = ((0, 'default'),
                      (1, 'vim'),
                      (2, 'sublime'),
                      )

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                unique=True,
                                verbose_name=_('Benutzer'),
                                related_name='userprofile',
                                on_delete=models.CASCADE)
    sites = models.ManyToManyField(Site, through=UserSite, blank=True)

    person = models.ForeignKey(
            Person,
            blank=True, null=True,
            on_delete=models.CASCADE)
    email_on_message = models.BooleanField(
            default=False,
            verbose_name="Email-Benachrichtigung bei Nachrichten")
    email_on_comment_answer = models.BooleanField(
            default=False,
            verbose_name="Email-Benachrichtigung bei Antwort" +
                         " auf meine Kommentare")
    codemirror_keymap = models.IntegerField(choices=KEYMAP_CHOICES, default=0)

    @property
    def is_staff_for_site(self):
        return (Site.objects.get_current()
                in self.sites.filter(
                    usersite__role__in=[UserSite.STAFF, UserSite.SUPERUSER]))

    @property
    def avatar_url(self):
        """Overwrite this Pybb method in order to use userena avatars"""
        return self.get_mugshot_url()

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)

        # register user for the "current" site if no sites are registered
        # so far
        if not self.sites.exists():
            if self.user.is_superuser:
                role = UserSite.SUPERUSER
            elif self.user.is_staff:
                role = UserSite.STAFF
            else:
                role = UserSite.USER
            us = UserSite(user=self, site=Site.objects.get_current(),
                          role=role)

            # pylint: disable=no-member
            us.save()

    def get_absolute_url(self):
        return reverse('pybb:user',
                       kwargs={'username': self.user.username})

    def __unicode__(self):
        return 'Profil von %(username)s' % {'username': self.user.username}

