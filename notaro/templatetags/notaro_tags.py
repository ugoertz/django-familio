# -*- coding: utf8 -*-

from __future__ import unicode_literals
from __future__ import division

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def brightness(gr):
    r = int(gr[1:3], 16)
    g = int(gr[3:5], 16)
    b = int(gr[5:7], 16)
    return 1 - (0.2126 * r + 0.7152 * g + 0.0722 * b) / 256


@register.filter
def datebadge(year):
    '''
    Return badge displaying the specified year.
    '''

    if not year:
        return ''

    gradient = [
            "#FF0000", "#FE001C", "#FD0038", "#FC0055", "#FB0071", "#FA008D",
            "#F900AA", "#F800C6", "#F700E2", "#F700FF", "#E100FF", "#CB00FF",
            "#B500FF", "#9F00FF", "#8900FF", "#7300FF", "#5D00FF", "#4800FF",
            "#3F1BFF", "#3637FF", "#2D52FF", "#246EFF", "#1B8AFF", "#12A5FF",
            "#09C1FF", "#00DDFF", "#07DFDF", "#0EE1BF", "#15E49F", "#1CE67F",
            "#23E85F", "#2AEB3F", "#31ED1F", "#38F000", "#50F000", "#69F100",
            "#82F200", "#9BF300", "#B4F400", "#CDF500", "#E6F600", "#FFF700",
            "#FFDA00", "#FFBE00", "#FFA200", "#FF8600", "#FF6900", "#FF4D00",
            "#FF3100", "#FF1500",
            ]
    y = (int(year) - 1600) // 10
    if y < 0:
        gr = gradient[0]
    elif y >= len(gradient):
        gr = gradient[-1]
    else:
        gr = gradient[y]

    color = '#ffffff' if brightness(gr) > 0.5 else '#000000'

    return mark_safe(' '.join([
            '<span class="badge cabin"',
            'style="background-color: %s; ' % gr,
            'color: %s;">%d</span>' % (color, year),
            ]))

