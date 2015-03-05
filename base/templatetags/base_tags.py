import re

from django import template
from django.conf import settings
from django.utils.functional import allow_lazy
from django.utils.encoding import force_unicode
from django.template import Node


register = template.Library()


# https://djangosnippets.org/snippets/569/
def strip_empty_lines(value):
    """Return the given HTML with empty and all-whitespace lines removed."""
    return re.sub(r'\n[ \t]*(?=\n)', '', force_unicode(value))
strip_empty_lines = allow_lazy(strip_empty_lines, unicode)


class GaplessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return strip_empty_lines(self.nodelist.render(context).strip())


def gapless(parser, token):
    """
    Remove empty and whitespace-only lines.  Useful for getting rid of those
    empty lines caused by template lines with only template tags and possibly
    whitespace.

    Example usage::

        <p>{% gapless %}
          {% if yepp %}
            <a href="foo/">Foo</a>
          {% endif %}
        {% endgapless %}</p>

    This example would return this HTML::

        <p>
            <a href="foo/">Foo</a>
        </p>

    """
    nodelist = parser.parse(('endgapless',))
    parser.delete_first_token()
    return GaplessNode(nodelist)
gapless = register.tag(gapless)


@register.simple_tag
def settings_value(name):
    if name in getattr(settings, 'ALLOWABLE_VALUES', []):
        return getattr(settings, name, '')
    return ''
