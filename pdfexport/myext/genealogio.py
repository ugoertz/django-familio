# -*- coding: utf8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from functools import partial
from docutils import nodes
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.parsers.rst import directives, Parser, Directive
from docutils.parsers.rst.directives.images import Image
import os
import os.path
import tempfile

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
# from django_markup.filter.rst_filter import RstMarkupFilter
from django.core.urlresolvers import reverse

# pylint: disable=import-error
from maps.models import CustomMap
from genealogio.models import Person
from genealogio.views import Sparkline
from genealogio.filter.rst_filter import genrst_roles
from notaro.models import Picture


class includepdf(nodes.image, nodes.Element):
    pass


def visit_includepdf(self, node):
    attrs = node.attributes
    placement = '[%s]' % attrs['placement'] if 'placement' in attrs else ''
    angle = 'angle=90, ' if 'rotate' in attrs else ''
    height = attrs.get('height', '23.5cm')
    caption = r'\caption{%s}' % attrs['caption'] if attrs['caption'] else ''
    if not height[-2:] in ['cm', 'mm', 'pt']:
        height += 'cm'

    self.body.append(
            r'''
\begin{figure}%s
\includegraphics[%sheight=%s, width=\textwidth, keepaspectratio]{%s}
%s
\end{figure}

''' % (placement, angle, height, os.path.basename(attrs['uri']), caption))


def depart_includepdf(self, node):
    pass


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
                nodelist = [nodes.image(
                    uri='/../../../' + img.image.__unicode__(),
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
                    uri='/../../../' + map.rendered.__unicode__(),
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
                                nodes.raw(
                                    '',
                                    '\n\n%s %s\n\n' % (
                                        m.get_label_tex(),
                                        m.get_description()),
                                    format="latex",
                                    **options))

            except ObjectDoesNotExist:
                nodelist = []
        else:
            # for now, ignore links to database objects here
            nodelist = [nodes.inline(rawtext, t, **options), ]
    except ImportError:
        msg = inliner.reporter.error(
                'Problem when evaluating handle: %s %s' % (text, rawtext, ),
                line=lineno)
        prb = inliner.problematic(text, rawtext, msg)
        return [prb], [msg]
    return nodelist, []


class FamilyTreePDF(Directive):

    # required arguments:
    # handle of a person
    # "pedigree" or "descendants
    required_arguments = 2
    optional_arguments = 0
    option_spec = {
            'generations': directives.positive_int,
            'rotate': directives.flag,
            'height': directives.unchanged,
            'placement': directives.unchanged,
            'caption': directives.unchanged,
            }

    def run(self):
        if self.arguments[1] == 'pedigree':
            generations_default = 3

            # for pedigree, use landscape mode by default, for descendants use
            # portrait mode by default:
            if 'rotate' in self.options:
                del self.options['rotate']
            else:
                self.options['rotate'] = True

        elif self.arguments[1] == 'descendants':
            generations_default = 2
        else:
            return []
        handle = self.arguments[0]

        if 'caption' not in self.options:
            try:
                p = Person.objects.get(handle=handle)
            except ObjectDoesNotExist:
                return []
            if self.arguments[1] == 'pedigree':
                self.options['caption'] =\
                        'Ahnentafel für %s' % p.get_primary_name()
            elif self.arguments[1] == 'descendants':
                self.options['caption'] =\
                        'Nachkommen von %s' % p.get_primary_name()

        _, fn = tempfile.mkstemp(
                dir=os.path.join(settings.MEDIA_ROOT, 'latex'),
                suffix='.pdf',
                prefix='phantom')
        _, fn2 = tempfile.mkstemp(
                dir=os.path.join(settings.MEDIA_ROOT, 'latex'),
                suffix='.pdf',
                prefix='phantom')
        url = 'http://%s%s' % (
                Site.objects.get_current().domain,
                reverse('%s-pdf' % self.arguments[1], kwargs={
                    'handle': handle,
                    'generations':
                    self.options.get('generations', generations_default), }))
        os.system("phantomjs %s '%s' %s"
                  % (settings.PHANTOMJS_SCRIPT, url, fn))
        os.system("pdfcrop %s %s" % (fn, fn2))

        return [
                includepdf(
                    uri='/../../../latex/%s' % os.path.basename(fn2),
                    **self.options), ]


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
        self.arguments[0] = '/../../../latex/%s' % filename

        return super(SparklineImg, self).run()


# pylint: disable=no-member
def setup(app):
    app.add_node(includepdf, latex=(visit_includepdf, depart_includepdf))
    for role in genrst_roles:
        app.add_role(role, partial(
            get_text,
            model=genrst_roles[role]['model'],
            extra=genrst_roles[role].get('extra', '')))
    app.add_directive('familytree', FamilyTreePDF)
    app.add_directive('sparklineimg', SparklineImg)

