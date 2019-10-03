# -*- coding: utf8 -*-

from django.contrib.sites.models import Site
from django.test import TestCase
import factory

from accounts.tests import UserProfileFactory, UserFactory
from .models import Note


RST = '''
This is a test note. *This is a sentence in italics.* Now a **word** in bold face.

Heading
-------

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At
vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren,
no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit
amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut
labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam
et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata
sanctus est Lorem ipsum dolor sit amet.

* list item 1
* list item 2
* list item 3

Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod
tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At
vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren,
no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit
amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut
labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam
et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata
sanctus est Lorem ipsum dolor sit amet.
'''

RST_WITH_ERRORS = '''
This is another note. The RestructuredText formatting contains some errors.

This is a heading
------------

This is the continuation of the text.
'''


class NoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Note

    title = factory.Sequence(lambda n: "Note %s - title" % n)
    link = factory.Sequence(lambda n: '/note%s' % n)
    text = RST

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        current_site = Site.objects.get_current()
        self.sites.add(current_site)


class NoteDetailViewTest(TestCase):

    def setUp(self):
        self.note1 = NoteFactory()
        self.user = UserFactory()
        self.admin = UserFactory(is_superuser=True)

    def test_basics(self):
        self.assertTrue(
                self.client.login(username=self.user.username,
                                  password='password'))
        response = self.client.get('/notes/all/')
        self.assertContains(response, self.note1.title)

        # pylint: disable=no-member
        response_id = self.client.get('/notes/note-view/%d/' % self.note1.id)
        self.assertContains(response_id, 'ipsum dolor sit amet')

        response_link = self.client.get('/n%s' % self.note1.link)
        self.assertContains(response_link, 'ipsum dolor sit amet')

    def test_note_with_rst_errors(self):
        self.note2 = NoteFactory(text=RST_WITH_ERRORS)
        self.assertTrue(
                self.client.login(username=self.user.username,
                                  password='password'))
        response = self.client.get('/notes/all/')
        self.assertContains(response, self.note1.title)
        self.assertContains(response, self.note2.title)
        response_link = self.client.get('/n%s' % self.note2.link)
        self.assertContains(response_link, 'continuation of the')
        self.assertContains(response_link,
                'System Message: WARNING')

