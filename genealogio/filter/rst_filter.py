from functools import partial
from docutils import nodes
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.parsers.rst import roles, Parser
from django.core.exceptions import ObjectDoesNotExist
from django_markup.filter.rst_filter import RstMarkupFilter
from django.core.urlresolvers import reverse
from ..models import Person, Place, Event, Family
from notaro.models import Picture, Source


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
    's': {'model': Source, },
    'i': {'model': Picture, },
    'it': {'model': Picture, },
    'is': {'model': Picture, },
    'im': {'model': Picture, },
    'ib': {'model': Picture, },
    'il': {'model': Picture, },
}


class GenRstMarkupFilter(RstMarkupFilter):
    """RstMarkupFilter adapted to the genealogio app.

    This filter has the following custom roles:

    - :p:`OptionalTextToBeInserted HandleToPerson` Everything before the space
      will be inserted into the text; with a link to the person specified by
      the handle.
    """

    title = 'genReStructuredText'

    def __init__(self, *args, **kwargs):
        super(GenRstMarkupFilter, self).__init__(*args, **kwargs)
        for role in genrst_roles:
            roles.register_local_role(role, getattr(self, '%s_role' % role))


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
                reference = nodes.reference('', '')
                reference['refuri'] = reverse(
                        'picture-detail',
                        kwargs={'pk': img.id, })
                image_node = nodes.image(
                    uri=img.image.version_generate(version).url,
                    **options)
                reference.append(image_node)
                nodelist = [reference, ]
                if img.caption:
                    settings = OptionParser(components=(Parser,))\
                            .get_default_values()
                    parser = Parser()
                    document = new_document('caption', settings)
                    parser.parse(img.get_caption(), document)
                    nodelist.extend(document.children)
            except ObjectDoesNotExist:
                nodelist = []
        else:
            handle = text.split(' ')[-1]
            try:
                if name.startswith('s'):
                    # Look up Source object by id
                    p = model.objects.get(pk=handle)
                else:
                    # Look up all other model instances by handle
                    p = model.objects.get(handle=handle)
                for f in extra:
                    t += f(p)
                nodelist = [nodes.reference(
                                rawtext, t,
                                refuri=p.get_absolute_url(), **options), ]
            except ObjectDoesNotExist:
                # for now, assume that this is because that object exists only
                # on another site; so fail silently
                # FIXME: check that handle exists on some site
                nodelist = [nodes.inline(rawtext, t, **options), ]
    except:
        msg = inliner.reporter.error('Problem when evaluating handle',
                                     line=lineno)
        prb = inliner.problematic(text, rawtext, msg)
        return [prb], [msg]
    return nodelist, []

# pylint: disable=no-member
for role in genrst_roles:
    setattr(GenRstMarkupFilter, '%s_role' % role,
            staticmethod(partial(get_text,
                         model=genrst_roles[role]['model'],
                         extra=genrst_roles[role]['extra']
                         if 'extra' in genrst_roles[role] else [])))
    setattr(getattr(GenRstMarkupFilter, '%s_role' % role), 'options', {})
    setattr(getattr(GenRstMarkupFilter, '%s_role' % role), 'content', False)

