from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
from os import path
sys.path.append(path.join(path.dirname(path.realpath(__file__)), '..'))

from ansible.errors import AnsibleError
from utils import dicts


class ParametersSpec(dict):

    def __init__(self, param_spec, vars, args):
        super(ParametersSpec, self).__init__(args)

        self._param_spec = param_spec
        self._task_vars = vars
        self._task_args = args

        # Initialize required_one_of property
        self.required_one_of = dicts.get_value(param_spec, 'required_one_of', default=[])

        # Initialize required properties
        self.required = []
        for spec in param_spec.keys():
            if( type(param_spec[spec]) == dict
                and dicts.get_value(param_spec[spec], 'required', default=False) ):

                self.required.append(spec)

        # Run parameters checks
        self._check_required()
        self._check_required_one_of()
        self._check_values()

    def _check_required(self):
        ''' check required parameters '''

        # Looping on each required parameter
        # If one of the parameters is not defined
        # or has no value then raise error
        for arg in self.required:
            if( arg not in self.keys()
                or len(self[arg]) == 0 ):
                    raise AnsibleError('At least one of the "{0}" parameter is missing.'.format('", "'.join(self.required)))

    def _check_required_one_of(self):
        ''' check required_one_of parameters '''

        # Looping on each parameter that
        # should have at least once specified
        # If one of the parameters is not defined
        # or has no value then raise error
        result = False
        for arg in self.required_one_of:
            if( arg in self.keys()
                and len(self[arg]) > 0 ):
                    result = True
                    break

        if not result:
            raise AnsibleError('At least one of the "{0}" parameter is required.'.format('", "'.join(self.required_one_of)))

    def _check_values(self):
        ''' check plugin parameters validity '''

        result = False
        errors = []

        # Looping on each parameter specification
        for arg in self._param_spec.keys():

            # Checking that parameter is defined and has values
            if arg in self:

                    # Checking that each value have a correct type
                    for variable in self[arg]:
                        variable_valid = False

                        # Looping on each valid parameters specification
                        for variable_type in self._param_spec[arg]['type']:

                            # If the type of the variable is the same that the one
                            # specified in the parameter specification then
                            # break the loop
                            if type(variable) == variable_type:
                                variable_valid = True
                                break

                            # If the type of the variable specification is a list of
                            # type then check if the variable has the same length
                            # and that all the variable types are the same that
                            # the parameter specification.
                            # If so break the loop
                            elif type(variable_type) == list:
                                if len(variable) == len(variable_type):
                                    i=0
                                    type_valid = True
                                    for variable_type in variable_type:
                                        if type(variable[i]) != variable_type:
                                            type_valid = False
                                            break
                                        i += 1
                                    if type_valid:
                                        variable_valid = True
                                        break

                        # If the variable does not match any parameter specification
                        # then add an error intp the error list
                        if not variable_valid:
                            errors.append('{0}> {1} has not the correct format'.format(arg, variable))

        # If there is at least on parameter specified
        #   If there is no error then return True
        #   If there are errors then raise the error list
        # If there is no parameter specified then raise an error
        if len(errors) == 0:
            return True
        else:
            raise AnsibleError('\n'.join(errors))

    def __getitem__(self, key):
        ''' get the specified parameter values '''

        result = dicts.get_value(self._param_spec[key], 'default', default=None)

        if key in self._task_args:
            value = self._task_args[key]
            if value is not None:
                # make sure the parameter items are a list
                result = value
                if( dicts.get_value(self._param_spec[key], 'tolist', default=False)
                    and not isinstance(result, list) ):
                    result = [result]

        return result