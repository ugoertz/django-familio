# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver, FirefoxProfile
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

    profile = factory.RelatedFactory(UserProfileFactory, 'user')



