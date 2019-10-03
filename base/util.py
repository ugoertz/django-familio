# -*- coding: utf8 -*-

import sys


def eprint(*args, **kwargs):
    '''
    Print to stderr. Use for debugging.
    '''

    kwargs.update({'file': sys.stderr, })
    print(*args, **kwargs)




