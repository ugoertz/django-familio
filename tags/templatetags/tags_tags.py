# -*- coding: utf8 -*-

from django import template
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from ..models import CustomTag

register = template.Library()


@register.simple_tag
def get_obj_list(app, model, obj):
    '''
    Return list of all objects of type app.model tagged with a tag pointing to
    obj (an object in the db, e.g. Person, Family, ...).
    '''

    try:
        return apps.get_model(app, model).objects.filter(
                tags__slug='%s.%s-%d' % (
                    obj._meta.app_label, obj._meta.model_name, obj.id))
    except:
        return []


@register.simple_tag
def get_tag_list(app, model, tag):
    '''
    Return list of all objects of type app.model tagged with the tag "tag".
    '''

    try:
        return apps.get_model(app, model).objects.filter(tags__slug='%s' % tag)
    except:
        return []


@register.filter
def as_tag_text(slug):
    try:
        tag = CustomTag.objects.get(slug=slug)
        return tag.as_tag_text()
    except ObjectDoesNotExist:
        raise Http404
