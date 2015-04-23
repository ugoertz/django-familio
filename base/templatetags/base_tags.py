import re

from django import template
from django.conf import settings
from django.utils.functional import allow_lazy
from django.utils.encoding import force_unicode
from django.template import Node
from django.template.defaulttags import CommentNode
from django.template.loader_tags import do_include


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


@register.tag('include_if_exists')
def do_include_maybe(parser, token):
    "Source: http://stackoverflow.com/a/18951166/15690"
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            "%r tag takes at least one argument: "
            "the name of the template to be included." % bits[0])

    try:
        silent_node = do_include(parser, token)
    except template.TemplateDoesNotExist:
        # Django < 1.7
        return CommentNode()

    _orig_render = silent_node.render
    def wrapped_render(*args, **kwargs):
        try:
            return _orig_render(*args, **kwargs)
        except template.TemplateDoesNotExist:
            return CommentNode()
    silent_node.render = wrapped_render
    return silent_node
