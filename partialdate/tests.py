# -*- coding: utf8 -*-

from django.test import TestCase

from .fields import PartialDate

class PartialDateTests(TestCase):

    def test_create_partialdate(self):
        pd1 = PartialDate(2000, 1, 1)
        self.assertEqual(pd1.year, 2000)
        self.assertEqual(pd1.month, 1)
        self.assertEqual(pd1.day, 1)
        self.assertEqual(pd1.isoformat(), '2000-01-01')
        self.assertEqual(str(pd1), '2000-01-01')
        self.assertEqual(pd1.weekday, 5)

        pd2 = PartialDate(2001, 1)
        self.assertEqual(pd2.year, 2001)
        self.assertEqual(pd2.month, 1)
        self.assertEqual(pd2.day, None)
        self.assertEqual(pd2.isoformat(), '2001-01')

