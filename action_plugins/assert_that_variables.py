from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from os import path
sys.path.append(path.join(path.dirname(path.realpath(__file__)), '..'))

from ansible.module_utils.basic import AnsibleModule
from ansible.errors import AnsibleError
from ansible.playbook.conditional import Conditional
from ansible.plugins.action import ActionBase
from ansible.module_utils.six import string_types
from ansible.parsing.yaml.objects import AnsibleUnicode
from filter_plugins import variables
from utils import parameters
from utils import dicts


class ActionModule(ActionBase):
    ''' handler for assert_that_variables operations '''

    _ASSERT_ARGS_SPEC = {
        'HasValue': {
            'type': [ AnsibleUnicode, [AnsibleUnicode], [AnsibleUnicode,dict] ],
            'default': [],
            'tolist': True
            },
        'HasIntValue': {
            'type': [ AnsibleUnicode, [AnsibleUnicode], [AnsibleUnicode,dict] ],
            'default': [],
            'tolist': True
            },
        'HasBoolValue': {
            'type': [ AnsibleUnicode, [AnsibleUnicode], [AnsibleUnicode,dict] ],
            'default': [],
            'tolist': True
            },
        'HasValueIn':   {
            'type': [ [AnsibleUnicode,list], [AnsibleUnicode,list,dict] ],
            'default': [],
            'tolist': True
            },
        'MutuallyHasValueOrNot': {
            'type': [ list, [list,dict] ],
            'default': [],
            'tolist': True
            }
    }
    _EXTRA_ARGS_SPEC = {
        'fail_msg': {
            'type': str,
            'default': 'Assertion failed'
            },
        'success_msg': {
            'type': str,
            'default': 'All assertions passed'
            },
        'required_one_of' : [
            'HasValue', 'HasIntValue', 'HasBoolValue', 'HasValueIn', 'MutuallyHasValueOrNot']
    }
    _ARGS_SPEC = dicts.merge(_ASSERT_ARGS_SPEC, _EXTRA_ARGS_SPEC)
    _VALID_ARGS = frozenset(tuple(_ASSERT_ARGS_SPEC.keys()) + tuple(_EXTRA_ARGS_SPEC.keys()))

    def _init_global_vars(self, tmp=None, task_vars=None):
        ''' initialize class variables '''

        # Initialize simple vars
        self._task_vars = dict() if task_vars is None else task_vars

        # Initialize tasj result
        self._result = super(ActionModule, self).run(tmp, task_vars)
        self._result['_ansible_verbose_always'] = True
        self._result['changed'] = False
        self._result['failed'] = False

        del tmp  # tmp no longer has any effect

        # Define an AnsibleModule object
        # To check parameters
        self._params = parameters.ParametersSpec(self._ARGS_SPEC, self._task_vars, self._task.args)

    def _do_all_assert(self):
        ''' perform all the asserts '''

        for arg in self._ASSERT_ARGS_SPEC:
            for param_value in self._params[arg]:

                # Parse all the parameters values
                # Defined variable name, extra condition
                # and valid values list
                variable = None
                variable_list = []
                values = []
                extra_cond = {}
                if arg == 'MutuallyHasValueOrNot':
                    variable_list = param_value
                    if len(param_value) == 2 and type(param_value[1]) == list:
                        variable_list = param_value[0]
                        extra_cond = param_value[1]
                elif arg == 'HasValueIn':
                    variable = param_value[0]
                    values = param_value[1]
                    if len(param_value) == 3:
                        extra_cond = param_value[2]
                else:
                    variable = param_value
                    if isinstance(variable, list):
                        variable = param_value[0]
                        if len(param_value) == 2:
                            extra_cond = param_value[1]

                # If there is no when condition or
                # if the when condition is evaluated
                # to True then performs the check
                if (  'when' not in extra_cond.keys() or
                      self._do_assert(extra_cond['when'], fill_result=False) ):

                    # Define allow empty params
                    allow_empty = (
                        variables.to_bool(extra_cond['allow_empty'], default=False)
                        if 'allow_empty' in extra_cond.keys()
                        else False )
                    allow_empty = ('not {0}|is_set or ' if allow_empty else '{0}|is_set and ').format(variable)

                    if arg == 'MutuallyHasValueOrNot':
                        self._do_assert((
                            '({0}|is_set) or (not {1}|is_set)'
                        ).format(
                            '|is_set and '.join(variable_list),
                            '|is_set and not '.join(variable_list)
                        ), arg)
                    elif arg == 'HasValueIn':
                        self._do_assert("{0}{1}|in_list(['{2}'])".format(
                            allow_empty,
                            variable,
                            "','".join(values)
                        ), arg)
                    else:
                        # Defined assert method to use
                        method = 'is_set'
                        if arg == 'HasIntValue':
                            method = 'is_int'
                        elif arg == 'HasBoolValue':
                            method = 'is_bool'

                        # Performing assertions
                        if self._do_assert('{0}{1}|{2}'.format(allow_empty, variable, method), arg):
                            for condition in extra_cond.keys():
                                if condition == 'min':
                                    self._do_assert('{0}{1}>={2}'.format(allow_empty, variable, extra_cond[condition]), arg)
                                elif condition == 'max':
                                    self._do_assert('{0}{1}<={2}'.format(allow_empty, variable, extra_cond[condition]), arg)

        # If no error found then return success message
        if not self._result['failed']:
            self._result['msg'] = self._params['success_msg']

    def _do_assert(self, condition, category="", fill_result=True):
        ''' perform a single assert and fill the result '''

        cond = Conditional(loader=self._loader)
        cond.when = [AnsibleUnicode(condition)]

        test_result = cond.evaluate_conditional(templar=self._templar, all_vars=self._task_vars)
        if fill_result and not test_result:
            self._result['failed'] = True
            self._result['evaluated_to'] = False
            if 'assertion' not in self._result.keys():
                self._result['assertion'] = []
            self._result['assertion'].append('{0}> {1}'.format(category, condition))
            self._result['msg'] = self._params['fail_msg']

        return test_result

    def run(self, tmp=None, task_vars=None):
        ''' run the action plugin '''

        # Initializing module global vars
        self._init_global_vars(tmp, task_vars)

        # Launch assertions
        self._do_all_assert()

        return self._result