# action_plugins

## Purpose

Action plugins act in conjunction with modules to execute the actions required by playbook tasks. They usually execute automatically in the background doing prerequisite work before modules execute.

Check to the following url to get more information:

* https://docs.ansible.com/ansible/2.5/plugins/action.html

## Plugins list

### assert_that_variables

This plugin is aimed at checking different variables types in one task.

#### Parameters

| Name | Comments |
|------|----------|
| HasValue | A string containing the name of a variable on which we should assert that it is defined, not none and is not an empty string. Alternatively, a list of string. |
| HasIntValue | A string containing the name of a variable on which we should assert that it is defined and it is an integer value. Alternatively, a list of string. |
| HasBoolValue | A string containing the name of a variable on which we should assert that it is defined and it is a boolean value. Alternatively, a list of string. |
| HasValueIn | A list containing at the first element the name of a variable and at the second element a list of values on which we should assert that the specified variable value should be a value from the list specified. Alternatively, a list of variable and values. |
| MutuallyHasValueOrNot | A list of variable names on which we should assert that they all have a value or they all have no value. Alternatively, a list of variables list. |

#### Extra condition

Extra condition is a list of properties containing extra instruction checks.

| Name | Apply to | Comments |
|------|----------|----------|
| min | HasIntValue | Check that an integer is greater or equals the specified value. |
| max | HasIntValue | Check that an integer is lower or equals the specified value. |
| allow_empty | HasIntValue, HasBoolValue, HasValueIn | When `yes` does not perform checks if the variable has not value. |
| when | All | Performs only checks when the specified condition is met. |

#### Samples

```yaml
assert_that_variables:
  HasValue:
    - variable_name                                                       # Simple check
    - [ variable_name ]                                                   # Simple check
    - [ variable_name, { when: 'condition' } ]                            # Check only when condition is true
  HasIntValue:
    - variable_name                                                       # Simple check
    - [ variable_name ]                                                   # Simple check
    - [ variable_name, { min: 0, max: 10 } ]                              # Extra check that value is between a range
    - [ variable_name, { allow_empty: yes } ]                             # Check only if variable is set
    - [ variable_name, { when: 'condition' } ]                            # Check only when condition is true
  HasBoolValue:
    - variable_name                                                       # Simple check
    - [ variable_name ]                                                   # Simple check
    - [ variable_name, { allow_empty: yes } ]                             # Check only if variable is set
    - [ variable_name, { when: 'condition' } ]                            # Check only when condition is true
  HasValueIn:
    - [ variable_name, ['value1', 'value2'] ]                             # Simple check
    - [ [ variable_name, ['value1', 'value2'] ], { allow_empty: yes } ]   # Check only if variable is set
    - [ [ variable_name, ['value1', 'value2'] ], { when: 'condition' } ]  # Check only when condition is true
  MutuallyHasValueOrNot:
    - [ variable_name, variable_name ]                                    # Simple check
    - [ [ variable_name, variable_name ], { when: 'condition' } ]         # Check only when condition is true
```