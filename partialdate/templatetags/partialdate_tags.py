# -*- coding: utf8 -*-

"""
Template tag to format partial dates.

See https://gitorious.org/wmbr-playback/wmbr-dj3000/source/f6ad6a8e947e60ecd097e196003e0400cd8d4829:partialdatefield
"""

from django import template
from django.conf import settings
from django.utils.formats import get_format
from django.utils.dateformat import DateFormat, re_formatchars, re_escaped
from django.utils.encoding import force_text

from ..fields import PartialDate

register = template.Library()


class IndeterminateDateValueException(Exception):
    """An indeterminate date property (used when formatting)."""
    pass


class ExceptionThrowingPartialDate(PartialDate):
    def __init__(self, dt):
        self._dt = dt

    def __getattr__(self, name):
        if name in ('_month', '_day') and\
                getattr(self.__getattribute__('_dt'), name) is None:
            raise IndeterminateDateValueException
        else:
            return getattr(self.__getattribute__('_dt'), name)


class PartialDateFormat(DateFormat):
    """Like DateFormat, but for PartialDates."""
    def __init__(self, dt):
        # Wrap dt with something which will throw
        # IndeterminateDateValueException when None is returned.
        super(PartialDateFormat, self).__init__(
            ExceptionThrowingPartialDate(dt))

    def format(self, formatstr):
        pieces = []
        trailing_indices = []
        for i, piece in enumerate(re_formatchars.split(force_text(formatstr))):
            if i % 2:
                try:
                    pieces.append(force_text(getattr(self, piece)()))
                    skip_literal = False
                except IndeterminateDateValueException:
                    skip_literal = True
                    trailing_indices.append(len(pieces) - 1)
            elif piece and not skip_literal:
                pieces.append(re_escaped.sub(r'\1', piece))
        trailing_indices.reverse()
        for i in trailing_indices:
            if i == len(pieces) - 1:
                # Remove dangling suffix literals.
                pieces.pop()
            elif i == 0:
                # Remove dangling prefix literals.
                pieces = pieces[1:]
        return ''.join(pieces)


@register.filter(is_safe=False)
def partial_date(value, arg=None):
    """
    Renders a PartialDateField according to the current locale using a
    date format similar to the date template tag.

    In order to support partial dates, formats will attempt to
    gracefully degrade by rendering indeterminate symbol values using
    the empty string.  Any constant string following such an empty
    string will also be dropped, as will constant strings preceding
    such a string IF all subsequent formats are also empty, or the
    character run is the first such format in the string.

    For example, the format pattern "F j, y" will render as follows
    in the en_US locale:

    INPUT: "2013-06-12"
    OUTPUT: "June 12, 2013"

    INPUT: "2013-06"
    OUTPUT: "June 2013"
    (note that the literal ", " following the indeterminate "d" symbol
    is skipped)

    INPUT: "2013"
    OUTPUT: "2013"
    """
    if value in (None, ''):
        return ''

    if arg is None:
        arg = settings.DATE_FORMAT

    try:
        arg = get_format(arg or 'DATE_FORMAT')
    except AttributeError:
        # It's okay.  arg is probably an acceptable format.
        pass

    try:
        return PartialDateFormat(value).format(arg)
    except AttributeError:
        return ''
