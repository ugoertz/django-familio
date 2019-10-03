# -*- coding: utf8 -*-

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase

import factory

from .models import UserProfile


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    first_name = factory.Sequence(lambda n: "First%s" % n)
    last_name = factory.Sequence(lambda n: "Last%s" % n)
    email = factory.Sequence(lambda n: "email%s@example.com" % n)
    username = factory.Sequence(lambda n: "john%s" % n)
    password = make_password("password")
    is_staff = False


class UserProfileTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_userprofile_created(self):
        self.assertTrue(
                self.client.login(username=self.user.username,
                                  password='password'))

        # pylint: disable=no-member
        self.assertTrue(Site.objects.get_current()
                in self.user.userprofile.sites.all())


