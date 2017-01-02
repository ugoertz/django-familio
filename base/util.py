# -*- coding: utf8 -*-

from __future__ import unicode_literals, print_function


def eprint(*args, **kwargs):
    '''
    Print to stderr. Use for debugging.
    '''

    print(*args, file=sys.stderr, **kwargs)




