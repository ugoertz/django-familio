# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from django import template
from django.db.models.loading import get_model

from maps.models import Place
from genealogio.models import Event, Family, Person
from notaro.models import Document, Picture

from ..models import CustomTag

register = template.Library()

@register.assignment_tag
def get_obj_list(app, model, obj):
    '''
    Return list of all objects of type app.model tagged with a tag pointing to
    obj (an object in the db, e.g. Person, Family, ...).
    '''

    return get_model(app, model).objects.filter(
            tags__slug='%s.%s-%d' % (
                obj._meta.app_label, obj._meta.model_name, obj.id))


@register.assignment_tag
def get_tag_list(app, model, tag):
    '''
    Return list of all objects of type app.model tagged with the tag "tag".
    '''

    return get_model(app, model).objects.filter(tags__slug='%s' % tag)


@register.filter
def as_tag_text(slug):
    tag = CustomTag.objects.get(slug=slug)
    return tag.as_tag_text()