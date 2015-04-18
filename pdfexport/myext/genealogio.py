from __future__ import absolute_import

from functools import partial
from docutils import nodes
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.parsers.rst import roles, Parser
from docutils.parsers.rst.directives.images import Image
import os
import os.path
import tempfile
import urllib

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
# from django_markup.filter.rst_filter import RstMarkupFilter
from django.core.urlresolvers import reverse

# pylint: disable=import-error
from genealogio.models import Person, Place, Event, Family
from genealogio.views import Sparkline
from notaro.models import Picture


genrst_roles = {
    'p': {'model': Person, },
    'pd': {'model': Person,
           'extra': [lambda p: ' (%s - %s)' %
                               (p.datebirth.year if p.datebirth else '',
                                p.datedeath.year if p.datedeath else '', )
                     ], },
    'l': {'model': Place, },
    'e': {'model': Event, },
    'f': {'model': Family, },
    'i': {'model': Picture, },
    'it': {'model': Picture, },
    'is': {'model': Picture, },
    'im': {'model': Picture, },
    'ib': {'model': Picture, },
    'il': {'model': Picture, },
}


def get_text(name, rawtext, text, lineno, inliner,
             options={}, content=[],
             model='', extra=[]):
    try:
        t = ' '.join(text.split(' ')[:-1])
    except:
        msg = inliner.reporter.error(
            'Problem when evaluating :%s: role' % name, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    # pylint: disable=no-member
    try:
        if name.startswith('i'):
            if len(name) > 1:  # check for size parameter
                version = {'t': 'thumbnail',
                           's': 'small',
                           'm': 'medium',
                           'b': 'big',
                           'l': 'large', }[name[1]]
            else:
                version = 'medium'

            try:
                img = Picture.objects.get(id=int(text))
                nodelist = [nodes.image(uri='/../media/' + img.image.__unicode__(),
                                        **options), ]
                if False and img.caption:
                    settings = OptionParser(components=(Parser,))\
                            .get_default_values()
                    parser = Parser()
                    document = new_document('caption', settings)
                    parser.parse(img.get_caption(), document)
                    nodelist[0].children.extend(document.children)
            except ObjectDoesNotExist:
                nodelist = []
        else:
            handle = text.split(' ')[-1]
            # try:
            #     p = model.objects.get(handle=handle)
            #     for f in extra:
            #         t += f(p)
            #     nodelist = [nodes.reference(
            #                     rawtext, t,
            #                     refuri=p.get_absolute_url(), **options), ]
            # except ObjectDoesNotExist:
            #     # for now, assume that this is because that object exists only
            #     # on another site; so fail silently
            #     # FIXME: check that handle exists on some site
            nodelist = [nodes.inline(rawtext, t, **options), ]
    except:
        msg = inliner.reporter.error('Problem when evaluating handle',
                                     line=lineno)
        prb = inliner.problematic(text, rawtext, msg)
        return [prb], [msg]
    return nodelist, []


class SparklineImg(Image):

    required_arguments = 1

    def run(self):
        lateximagedir = os.path.join(settings.MEDIA_ROOT, 'latex')

        # fetch png from specified url and save in temporary file
        _, _, _, pk, fr, to, _ = self.arguments[0].split('/')
        filename = 'img-%s-%s-%s.png' % (pk, fr, to)
        if not os.path.exists(os.path.join(lateximagedir, filename)):
            surface = Sparkline.get_image(pk, fr, to, width=5120, height=320)
            surface.write_to_png(os.path.join(lateximagedir, filename))

        # change argument so as to point to our temporary file
        self.arguments[0] = '/../media/latex/%s' % filename

        return super(SparklineImg, self).run()


# pylint: disable=no-member
def setup(app):
    for role in genrst_roles:
        app.add_role(role, partial(get_text,
                                   model=genrst_roles[role]['model'],
                                   extra=genrst_roles[role].get('extra', '')))
    app.add_directive('sparklineimg', SparklineImg)

