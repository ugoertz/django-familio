# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver, FirefoxProfile
import factory

from accounts.models import UserProfile
from accounts.tests import UserProfileFactory, UserFactory
from notaro.tests import NoteFactory, RST_WITH_ERRORS


class LoginTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(LoginTest, cls).setUpClass()

        profile = FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'de')
        cls.selenium = WebDriver(profile)
        cls.selenium.implicitly_wait(3)

    def setUp(self):
        # TODO: In Django 1.8, will be able to use setUpTestData
        self.user = UserFactory()
        self.admin = UserFactory(is_superuser=True)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LoginTest, cls).tearDownClass()

    def login(self, u):
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self.assertIn('Familiengeschichte', self.selenium.title)

        username_input = self.selenium.find_element_by_id("id_identification")
        username_input.send_keys(u.username)
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys('password')
        self.selenium.find_element_by_id('id_submitbutton').click()

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
        self.login(self.user)
        self.assertNotIn('korrekten Benutzername', self.selenium.page_source)
        self.assertIn(self.user.username, self.selenium.page_source)

    def test_note_with_rst_errors_user(self):
        self.note2 = NoteFactory(text=RST_WITH_ERRORS)
        self.login(self.user)
        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('Alle Texte', body)
        self.assertIn(self.note2.title, body)

        self.selenium.get('%s%s' % (self.live_server_url, '/notes/all'))
        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn(self.note2.title, body)

        self.selenium.get('%s/n%s'
                % (self.live_server_url, self.note2.link))

        # pylint: disable=no-member
        self.selenium.get('%s/notes/note-view/%d'
                % (self.live_server_url, self.note2.id))

        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('continuation of the', body)
        self.assertNotIn('System Message: WARNING', body)

    def test_note_with_rst_errors_staff(self):
        self.login(self.admin)
        self.note2 = NoteFactory(text=RST_WITH_ERRORS)
        # pylint: disable=no-member
        self.selenium.get('%s/notes/note-view/%d'
                % (self.live_server_url, self.note2.id))

        self.selenium.get('%s/n%s'
                % (self.live_server_url, self.note2.link))
        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('continuation of the', body)
        self.assertNotIn('System Message: WARNING', body)

        self.selenium.find_element_by_id('errormsg').click()
        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('System Message: WARNING', body)

