# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from django import template

register = template.Library()

@register.assignment_tag(takes_context=True)
def get_user_is_admin(context):
    user = context['user']
    if (user and user.is_authenticated() and
            user.userprofile.is_staff_for_site):
        return True
    return False
