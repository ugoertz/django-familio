# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.test import TestCase
import factory

from .models import Family, Name, Person, PersonFamily


class NameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Name

    name = factory.Sequence(lambda n: "Familyname%s" % n)
    typ = Name.FAMILYNAME


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    name = factory.RelatedFactory(NameFactory, 'person')
    handle = factory.Sequence(lambda n: "P_%s" % n)
    gender_type = Person.UNKNOWN

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        current_site = Site.objects.get_current()
        self.sites.add(current_site)


class FamilyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Family

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        current_site = Site.objects.get_current()
        self.sites.add(current_site)


class PersonTest(TestCase):

    def test_add_person(self):
        p = PersonFactory()
        self.assertEqual(unicode(p), '  %s' % p.handle)

    def test_get_children(self):
        father = PersonFactory()
        mother = PersonFactory()
        child1 = PersonFactory()
        child2 = PersonFactory()
        nonchild = PersonFactory()

        # pylint: disable=no-member
        family = FamilyFactory(father=father, mother=mother)
        PersonFamily.objects.create(person=child1, family=family)
        PersonFamily.objects.create(person=child2, family=family)

        # pylint: disable=no-member
        self.assertTrue(child1 in family.get_children())
        self.assertTrue(child2 in family.get_children())
        self.assertFalse(nonchild in family.get_children())





