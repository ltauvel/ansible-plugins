from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from os import path
sys.path.append(path.join(path.dirname(path.realpath(__file__)), '..'))

from filter_plugins import variables

def format_bool(value, when_true='true', when_false='false'):
    ''' return the 'when_false' value if 'value' is False else return the 'when_true' '''

    if variables.to_bool(value, default=False):
        return when_true
    else:
        return when_false

def format_string(value, when_not_set='', enclosure_char=''):
    ''' return the 'when_not_set' value if the 'value' is undefined, none, or empty string else returns the value enclosed by the 'enclosure_char' '''

    if variables.to_default(value, default=None) is None:
        return when_not_set
    else:
        return '{0}{1}{0}'.format(enclosure_char, value)

class FilterModule(object):

    def filters(self):
        return {
            'format_string': format_string,
            'format_bool': format_bool,
        }
