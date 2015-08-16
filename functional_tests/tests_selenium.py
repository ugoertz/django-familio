# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import os
import os.path

from django.contrib.sites.models import Site
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.core.urlresolvers import reverse
from selenium.webdriver.firefox.webdriver import WebDriver, FirefoxProfile

from accounts.models import UserSite
from accounts.tests import UserFactory
from genealogio.models import PersonFamily
from genealogio.tests import FamilyFactory, PersonFactory
from notaro.tests import NoteFactory, RST_WITH_ERRORS

# pylint: disable=no-member


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

        self.selenium.get(
                '%s/n%s' % (self.live_server_url, self.note2.link))

        self.selenium.get(
                '%s/notes/note-view/%d'
                % (self.live_server_url, self.note2.id))

        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('continuation of the', body)
        self.assertNotIn('System Message: WARNING', body)

    def test_note_with_rst_errors_staff(self):
        self.login(self.admin)
        self.note2 = NoteFactory(text=RST_WITH_ERRORS)

        self.selenium.get(
                '%s/notes/note-view/%d'
                % (self.live_server_url, self.note2.id))

        self.selenium.get(
                '%s/n%s'
                % (self.live_server_url, self.note2.link))
        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('continuation of the', body)
        self.assertNotIn('System Message: WARNING', body)

        self.selenium.find_element_by_id('errormsg').click()
        body = self.selenium.find_element_by_tag_name('body').text
        self.assertIn('System Message: WARNING', body)

    def test_login_for_different_usersites(self):
        user1 = UserFactory(is_staff=True)

        usersites = user1.userprofile.usersite_set.all()
        self.assertEqual(len(usersites), 1)

        # make user1 a user only for a site different from current
        site = Site.objects.create(domain="new")
        usersites[0].site_id = site.id
        usersites[0].save()

        # check that login fails
        self.login(user1)
        self.assertIn('korrekten Benutzername', self.selenium.page_source)

    def test_login_for_different_status_depending_on_usersite_failure(self):
        user1 = UserFactory(is_staff=True)

        # make user1 a non-staff user on current site:
        usersite = user1.userprofile.usersite_set.get(
                site=Site.objects.get_current())
        usersite.role = UserSite.USER
        usersite.save()

        # make user1 a staff user on a different site
        site = Site.objects.create(domain="new")
        UserSite.objects.create(
                user=user1.userprofile, site=site, role=UserSite.STAFF)

        # login to current site should work
        self.login(user1)
        self.assertNotIn('korrekten Benutzername', self.selenium.page_source)
        self.assertIn(user1.username, self.selenium.page_source)

        # but should not have staff status here (test for link to admin not
        # being displayed in menu)
        self.assertNotIn("Verwaltungsbereich", self.selenium.page_source)

    def test_login_for_different_status_depending_on_usersite_success(self):
        user1 = UserFactory(is_staff=True)

        # since is_staff is True, user1 should have staff role for current site
        usersite = user1.userprofile.usersite_set.get(
                site=Site.objects.get_current())
        self.assertEqual(usersite.role, UserSite.STAFF)

        # login to current site should work
        self.login(user1)
        self.assertNotIn('korrekten Benutzername', self.selenium.page_source)
        self.assertIn(user1.username, self.selenium.page_source)

        # and should have staff status here (test for link to admin being
        # displayed in menu)
        self.assertIn("Verwaltungsbereich", self.selenium.page_source)

    def test_send_invitation_email(self):
        self.login(self.user)

        self.selenium.get('%s/accounts/invite/' % self.live_server_url)
        self.assertIn('mindestens die Anrede', self.selenium.page_source)

        input = self.selenium.find_element_by_id('id_email')
        input.send_keys('aaa@example.com')

        input = self.selenium.find_element_by_id('id_first_name')
        input.send_keys('Django')

        input = self.selenium.find_element_by_id('id_last_name')
        input.send_keys('Reinhardt')

        submit = self.selenium.find_element_by_id('id_submit_invitation')
        submit.click()

        self.assertIn('verschickt', self.selenium.page_source)

        self.assertEqual(len(mail.outbox), 1)

        site = Site.objects.get_current()
        self.assertEqual(
                mail.outbox[0].subject,
                'Einladung von %s' % site.domain)

    def test_some_genealogio_views(self):
        self.login(self.user)

        # set up some persons and families
        grandfather_f = PersonFactory()
        grandmother_f = PersonFactory()
        grandfather_m = PersonFactory()
        grandmother_m = PersonFactory()
        father = PersonFactory()
        mother = PersonFactory()
        child1 = PersonFactory()
        child2 = PersonFactory()

        family = FamilyFactory(father=grandfather_f, mother=grandmother_f)
        PersonFamily.objects.create(person=father, family=family)
        family = FamilyFactory(father=grandfather_m, mother=grandmother_m)
        PersonFamily.objects.create(person=mother, family=family)

        family = FamilyFactory(father=father, mother=mother)
        PersonFamily.objects.create(person=child1, family=family)
        PersonFamily.objects.create(person=child2, family=family)

        self.selenium.get('%s/' % self.live_server_url)
        self.assertIn(child1.get_primary_name(), self.selenium.page_source)
        self.assertNotIn('Die neuesten Texte', self.selenium.page_source)
        self.assertNotIn('Die neuesten Kommentare', self.selenium.page_source)

        self.selenium.get(
                '%s' % self.live_server_url +
                reverse('person-detail', kwargs={'pk': child1.pk}))

        self.assertIn('Vater', self.selenium.page_source)
        self.assertIn('Mutter', self.selenium.page_source)

        self.selenium.get(
                '%s%s' % (
                    self.live_server_url,
                    reverse('person-detail', kwargs={'pk': grandfather_f.pk})))

        # father, mother should be unknown
        self.assertNotIn('Vater', self.selenium.page_source)
        self.assertNotIn('Mutter', self.selenium.page_source)

        # No comments so far
        self.assertIn(
                'Es gibt noch keine Kommentare', self.selenium.page_source)

        # add a comment
        inpt = self.selenium.find_element_by_id('id_content')
        inpt.send_keys('This is the first comment.')
        inpt.submit()
        self.assertIn(
                'This is the first comment.', self.selenium.page_source)
        self.assertNotIn(
                'Es gibt noch keine Kommentare', self.selenium.page_source)

        self.selenium.get(
                '%s' % self.live_server_url +
                reverse('person-list'))
        self.assertIn(child1.get_primary_name(), self.selenium.page_source)
        self.assertIn(child2.get_primary_name(), self.selenium.page_source)
        self.assertIn(father.get_primary_name(), self.selenium.page_source)
        self.assertIn(
                grandfather_f.get_primary_name(), self.selenium.page_source)
        self.assertIn(
                grandmother_m.get_primary_name(), self.selenium.page_source)
        self.assertIn(
                grandmother_f.get_primary_name(), self.selenium.page_source)

        self.selenium.get(
                '%s' % self.live_server_url +
                reverse('family-list'))
        # expect to see 3 families
        self.assertIn('3 Einträge', self.selenium.page_source)

        self.selenium.get('%s/' % self.live_server_url)
        self.assertIn(child2.get_primary_name(), self.selenium.page_source)
        self.assertIn('Die neuesten Kommentare', self.selenium.page_source)

    def test_upload_picture(self):
        user1 = UserFactory(is_staff=True)
        self.login(user1)

        self.selenium.get(
                '%s%s' % (self.live_server_url, reverse('picture-list')))
        self.assertIn('0 Einträge', self.selenium.page_source)

        inpt = self.selenium.find_element_by_css_selector('input#id_archive')
        inpt.send_keys(os.path.abspath('./functional_tests/static/white.png'))
        self.selenium.find_element_by_id('id_submit_upload').click()

        self.selenium.get(
                '%s%s' % (self.live_server_url, reverse('picture-list')))
        self.assertIn('1 Eintr', self.selenium.page_source)


