from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_value(name):
    if name in getattr(settings, 'ALLOWABLE_VALUES', []):
        return getattr(settings, name, '')
    return ''
