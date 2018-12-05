from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

def is_set(value):
    ''' return a boolean indicating if the value is undefined, none, or empty string '''
    return to_default(value) is not None

def is_int(value):
    ''' return a boolean indicating if the value is an integer or not '''
    try:
        int(to_default(value, 0))
        return True
    except:
        return False

def is_bool(value):
    ''' return a boolean indicating if the value is a boolean or not '''
    value = to_default(value, 'false')
    return (
        isinstance(value, bool)
        or (isinstance(value, (int, long)) and value == 1)
        or (isinstance(value, (basestring, str)) and value.lower().strip() in
            ['yes','no','true','false','0','1'])
    )

def in_list(value, values):
    ''' return a boolean indicating if the value is in the specified 'values' list '''
    return to_default(value) in values

def to_bool(value, default=False):
    ''' convert a the value to a boolean. Returns 'default' if value is not set '''
    value = to_default(value, default)
    if isinstance(value, bool):
        return value
    elif (isinstance(value, (int, long)) and value == 1):
        return True
    elif (isinstance(value, (basestring, str)) and value.lower().strip() in ['yes','true','1']):
        return True

    return False

def to_default(value, default=None):
    ''' return the 'default' value if the 'value' is undefined, none, or empty string '''
    from jinja2.runtime import Undefined

    if (isinstance(value, Undefined) or value is None
        or (isinstance(value, (basestring, str)) and value.strip() == '')
    ):
        return default
    else:
        return value

class FilterModule(object):

    def filters(self):
        return {
            'is_set': is_set,
            'is_int': is_int,
            'is_bool': is_bool,
            'in_list': in_list,
            'to_default': to_default,
            'to_bool': to_bool,
        }
