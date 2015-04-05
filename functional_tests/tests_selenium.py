# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver, FirefoxProfile
import factory

from accounts.models import UserProfile


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


class LoginTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(LoginTest, cls).setUpClass()

        profile = FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'de')
        cls.selenium = WebDriver(profile)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LoginTest, cls).tearDownClass()

    def test_failed_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertIn('Familiengeschichte', self.selenium.title)

        # no user with these credentials exists
        username_input = self.selenium.find_element_by_id("id_identification")
        username_input.send_keys('myuser')
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys('secret')
        self.selenium.find_element_by_id('id_submitbutton').click()
        self.assertIn('korrekten Benutzername', self.selenium.page_source)

    def test_successful_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertIn('Familiengeschichte', self.selenium.title)

        u = UserFactory()
        username_input = self.selenium.find_element_by_id("id_identification")
        username_input.send_keys(u.username)
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys('password')
        self.selenium.find_element_by_id('id_submitbutton').click()
        self.assertNotIn('korrekten Benutzername', self.selenium.page_source)
        self.assertIn(u.username, self.selenium.page_source)

