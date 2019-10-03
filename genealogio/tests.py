# -*- coding: utf8 -*-

from django.contrib.sites.models import Site
from django.test import TestCase
import factory

from .models import Family, Name, Person, PersonFamily

# pylint: disable=no-member


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
        self.assertEqual(str(p), ' %s' % p.handle)

    def test_get_children(self):
        father = PersonFactory()
        mother = PersonFactory()
        child1 = PersonFactory()
        child2 = PersonFactory()
        nonchild = PersonFactory()

        family = FamilyFactory(father=father, mother=mother)
        PersonFamily.objects.create(person=child1, family=family)
        PersonFamily.objects.create(person=child2, family=family)

        self.assertTrue(child1 in family.get_children())
        self.assertTrue(child2 in family.get_children())
        self.assertFalse(nonchild in family.get_children())

    def test_person_get_father_mother_ancestors_descendants(self):
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

        self.assertEqual(father, child1.get_father())
        self.assertEqual(mother, child2.get_mother())
        self.assertEqual(None, grandfather_f.get_father())
        self.assertEqual(None, grandfather_f.get_mother())

        self.assertIn(grandfather_f, child1.ancestors())
        self.assertIn(grandmother_f, child1.ancestors())
        self.assertIn(grandfather_m, child1.ancestors())
        self.assertIn(grandmother_m, child1.ancestors())
        self.assertIn(father, child1.ancestors())
        self.assertIn(mother, child1.ancestors())
        self.assertNotIn(child1, child1.ancestors())
        self.assertNotIn(child2, child1.ancestors())
        self.assertEqual(len(child2.ancestors()), 6)

        self.assertIn(child1, father.descendants())
        self.assertIn(child1, grandfather_m.descendants())

        self.assertEqual(len(grandfather_m.descendants()), 3)

        family = Family.objects.get(father=grandfather_f)
        self.assertIn(child1, family.get_grandchildren())
        self.assertIn(child2, family.get_grandchildren())
        self.assertNotIn(father, family.get_grandchildren())
        self.assertEqual(len(family.get_grandchildren()), 2)

    def test_person_resethandle(self):
        p = PersonFactory(last_name='Abcdefgh')
        self.assertTrue(p.handle.startswith('P_'))

        p.reset_handle()
        self.assertTrue(p.handle.startswith('P_'))
        self.assertTrue(p.handle.endswith('-%d' % p.id))
        self.assertIn(p.last_name, p.handle)
        handle = p.handle

        p.reset_handle()
        self.assertEqual(handle, p.handle)


