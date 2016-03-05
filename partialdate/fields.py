# -*- coding: utf-8 -*-

"""Custom fields for the genealogio models.

- PartialDateField: as DateField, but allow for "partial dates", i.e., year
  only, or year+month only

see https://gitorious.org/wmbr-playback/wmbr-dj3000/source/
f6ad6a8e947e60ecd097e196003e0400cd8d4829:partialdatefield
"""

from __future__ import unicode_literals

import datetime

from django.db import models
from django.core.exceptions import ValidationError


def string_to_partialdate(value):
    """Return the PartialDate value of the input"""
    if isinstance(value, PartialDate):
        return value
    elif isinstance(value, datetime.date):
        return PartialDate.fromdate(value)
    elif not value:
        return None

    # It's a string.
    try:
        args = [int(x) for x in value.split('-')]
    except:
        raise ValidationError(
                "Datum bitte im Format JJJJ-MM-TT angeben, " +
                "Monat und/oder Tag können ausgelassen werden.")
    if len(args) < 1 or len(args) > 3:
        raise ValidationError(
                "Datum bitte im Format JJJJ-MM-TT angeben, " +
                "Monat und/oder Tag können ausgelassen werden.")
    try:
        return PartialDate(*args)
    except ValueError:
        raise ValidationError(
                "Datum bitte im Format JJJJ-MM-TT angeben, " +
                "Monat und/oder Tag können ausgelassen werden.")


class PartialDate(object):
    """
    Like datetime.date, except that it may represent a
    partially-specified date (e.g. year, year-month, year-month-day)
    by refusing to specify the month and day, or just the day (or by
    passing "None" to the replace() instance method.
    """

    def __init__(self, year, month=None, day=None):
        """
        Create a new PartialDate object with the specified year (and
        optional month and day.  If month is not provided or None, the
        value of day is assumed to be None regardless of the
        argument's value.)
        """
        self._year = year
        self._month = month
        self._day = day

        # Is it a valid date?
        y = year
        m = month
        d = day
        if month is None:
            m = 1
            d = 1
        elif day is None:
            d = 1
        self._date = datetime.date(y, m, d)

    def __len__(self):
        return len('{0}'.format(datetime.MAXYEAR)) + 6

    def __cmp__(self, other):
        if not isinstance(other, PartialDate):
            # Typically this would mean that other is None
            # None should be less than any date (this is consistent with the
            # return values further on in cases where month or day are None.
            return 1

        if self.year < other.year:
            return -1
        if self.year > other.year:
            return 1
        if self.month < other.month:
            return -1
        if self.month > other.month:
            return 1
        if self.day < other.day:
            return -1
        if self.day > other.day:
            return 1
        return 0

    @classmethod
    def fromdate(cls, date):
        """Convert a datetime.date object to a PartialDate object."""
        return cls(date.year, date.month, date.day)

    @property
    def year(self):
        """The year of the PartialDate."""
        return self._year

    @property
    def month(self):
        """The month of the PartialDate.  May be None."""
        return self._month

    @property
    def day(self):
        """The day of the PartialDate.  May be None."""
        return self._day

    @property
    def weekday(self):
        """The weekday of the PartialDate.  May be None."""
        if self.month is not None and self.day is not None:
            return self.todate().weekday()
        else:
            return None

    def isoformat(self):
        """
        Serialize the partial date using the ISO date format.

        Examples:

        PartialDate(2003) == '2003'
        PartialDate(2003, 10) == '2003-10'
        PartialDate(2003, 10, 23) == '2003-10-23'
        """
        s = '{0:04}'.format(self._year)
        if self._month:
            s += '-{0:02}'.format(self._month)
            if self._day:
                s += '-{0:02}'.format(self._day)
        return s

    def todate(self):
        """
        Return the PartialDate as a datetime.date object with unspecified
        fields set to 1.
        """
        return self._date

    def __unicode__(self):
        """
        Return the ISO formatted date.  The following is always true:
        str(partialdate) == partialdate.isoformat()
        """
        return self.isoformat()


class PartialDateField(models.CharField):
    """
    A partially-specified date (e.g. year, year-month, year-month-day)
    stored in a CharField for ease of sorting.
    """

    description = "A partially-specified date (e.g. year, year-month, " +\
                  "year-month-day)"

    def __init__(self, *args, **kwargs):
        """Create the PartialDateField"""
        # + 6 for "-xx-xx"
        kwargs['max_length'] = len('{0}'.format(datetime.MAXYEAR)) + 6
        super(PartialDateField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PartialDateField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection, context):
        if not value:
            return value
        return PartialDate(*[int(x) for x in value.split('-')])

    def to_python(self, value):
        """Return the PartialDate value of the input"""
        return string_to_partialdate(value)

    def get_prep_value(self, value):
        """Return the string value of the PartialDate"""

        try:
            return value.isoformat()
        except:
            pass

        # maybe value is a string containing a PartialDate?
        try:
            pd = string_to_partialdate(value)
            return pd.isoformat()
        except:
            return ''

