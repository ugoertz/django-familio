from functools import partial
from docutils import nodes
from docutils.parsers.rst import roles
from django_markup.filter.rst_filter import RstMarkupFilter
from ..models import Person, Place, Event, Family
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
            print 'found i role', int(text)
            img = Picture.objects.get(id=int(text))
            print 'retrieved image'
            node = nodes.image(uri=img.image.version_generate(version).url,
                               **options)
        else:
            handle = text.split(' ')[-1]
            p = model.objects.get(handle=handle)
            for f in extra:
                t += f(p)
            node = nodes.reference('rawtext', t,
                                   refuri=p.get_absolute_url(), **options)
    except:
        msg = inliner.reporter.error('Problem when evaluating handle',
                                     line=lineno)
        prb = inliner.problematic(text, rawtext, msg)
        return [prb], [msg]
    return [node], []

# pylint: disable=no-member
for role in genrst_roles:
    setattr(GenRstMarkupFilter, '%s_role' % role,
            staticmethod(partial(get_text,
                         model=genrst_roles[role]['model'],
                         extra=genrst_roles[role]['extra']
                         if 'extra' in genrst_roles[role] else [])))
    setattr(getattr(GenRstMarkupFilter, '%s_role' % role), 'options', {})
    setattr(getattr(GenRstMarkupFilter, '%s_role' % role), 'content', False)

