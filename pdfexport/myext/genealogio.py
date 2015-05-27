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
from maps.models import Place, CustomMap
from genealogio.models import Person, Event, Family
from genealogio.views import Sparkline
from genealogio.filter.rst_filter import genrst_roles
from notaro.models import Document, Picture, Source


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
                img_options = {}
                img_options.update(options)
                try:
                    img_options['width'] = {
                            'thumbnail': '2cm',
                            'small': '4cm',
                            'medium': '6cm',
                            'big': '8cm', }[version]
                except KeyError:
                    pass
                nodelist = [nodes.image(uri='/../media/' + img.image.__unicode__(),
                                        **img_options), ]
                if img.caption:
                    settgs = OptionParser(components=(Parser,))\
                            .get_default_values()
                    parser = Parser()
                    document = new_document('caption', settgs)
                    try:
                        parser.parse(img.get_caption(), document)
                        nodelist[0].children.extend(document.children)
                    except:
                        pass
            except ObjectDoesNotExist:
                nodelist = []
        elif name.startswith('m'):
            # include custom map
            include_title = 't' in name[1:]
            include_description = 'd' in name[1:]
            include_legend = 'l' in name[1:]
            try:
                map = CustomMap.objects.get(id=int(text))
                image_node = nodes.image(
                    uri='/../media/' + map.rendered.__unicode__(),
                    **options)
                nodelist = [image_node, ]
                if include_title and map.title:
                    nodelist.append(nodes.paragraph('', map.title, **options))
                if include_description and map.description:
                    settgs = OptionParser(components=(Parser,))\
                            .get_default_values()
                    parser = Parser()
                    document = new_document('caption', settgs)
                    try:
                        parser.parse(map.description, document)
                        nodelist.extend(document.children)
                    except:
                        pass
                if include_legend:
                    for m in map.custommapmarker_set.all():
                        if m.description == '-':
                            continue
                        nodelist.append(
                                nodes.paragraph(
                                    '',
                                    '(%s) %s' % (m.label, m.get_description()),
                                    **options))

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
        msg = inliner.reporter.error('Problem when evaluating handle: %s %s' % (text, rawtext, ),
                                     line=lineno)
        prb = inliner.problematic(text, rawtext, msg)
        return [prb], [msg]
    return nodelist, []


class SparklineImg(Image):

    required_arguments = 1

    def run(self):
        lateximagedir = os.path.join(settings.MEDIA_ROOT, 'latex')

        # fetch png from specified url and save in temporary file
        url = self.arguments[0]

        if url.find('sparkline-person') != -1:
            _, _, _, pk, fampk, fr, to, _ = url.split('/')
            filename = 'img-%s-%s-%s-%s.png' % (pk, fampk, fr, to)
            kwargs = {'pk': pk, 'fampk': fampk, 'fr': fr, 'to': to, }
        elif url.find('sparkline-head') != -1:
            _, _, _, fampk, fr, to, _ = url.split('/')
            filename = 'img-head-%s-%s-%s.png' % (fampk, fr, to)
            kwargs = {'fampk': fampk, 'fr': fr, 'to': to, }
        elif url.find('sparkline-tlitem') != -1:
            _, _, _, tlid, fr, to, _ = url.split('/')
            filename = 'img-tlid-%s-%s-%s.png' % (tlid, fr, to)
            kwargs = {'tlid': tlid, 'fr': fr, 'to': to, }
        else:
            return []

        if not os.path.exists(os.path.join(lateximagedir, filename)):
            kwargs.update({'width': 5120, 'height': 320, })
            surface = Sparkline.get_image(**kwargs)
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

