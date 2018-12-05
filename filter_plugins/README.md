# callback_plugins

## Purpose

Callback plugins enable adding new behaviors to Ansible when responding to events. By default, callback plugins control most of the output you see when running the command line programs.

Check to the following url to get more information:

* https://docs.ansible.com/ansible/2.5/dev_guide/developing_plugins.html#callback-plugins
* https://docs.ansible.com/ansible/2.7/plugins/callback.html

## Plugins list

### variables

#### to_default

This filter is inspired from the Ansible `default` filter but does not act only on undefined variables. It converts undefined, none and empty strings to a default value.

Parameters:

* `default`: The value to return if variable has not been set. Default: `none`.

Usage:

```jinja
variable_name | to_default              # Returns none if variable is empty
variable_name | to_default('value')     # Returns 'value' if variable is empty
variable_name | to_default(0)           # Returns 0 if variable is empty
variable_name | to_default(True)        # Returns True if variable is empty
```

#### to_bool

Convert the specified variable value to boolean. If the variable cannnot be converted to boolean then return `False` by default.

Parameters:

* `default`: The value to return if variable has not been set. Default: `False`.

Usage:

```jinja
variable_name | to_bool        # Returns converted value or False if conversion failed
variable_name | to_bool(True)  # Returns converted value or True if conversion failed
```

#### is_set

This filter is returns True if a variable is defined, not none and not an empty string.

Usage:

```jinja
variable_name | is_set
```

#### is_int

This filter is returns True if a variable is contains an integer value.

Usage:

```jinja
variable_name | is_int
```

#### is_bool

This filter is returns True if a variable is contains a boolean value.

Usage:

```jinja
variable_name | is_bool
```

#### in_list

This filter is returns True if the specified values list containes the variable value.

Usage:

```jinja
variable_name | in_list(['value1', 'value2'])
```

### formats

#### format_string

This filter returns value enclosed with 'enclosure_char' characters. It return a 'when_not_set' value if the variable is not set.

Parameters:

* `when_not_set`: The value to return if variable has not been set. Default: `none`.
* `enclosure_char`: A string used to enclose value if variable has been set.

Usage:

```jinja
variable_name | format_string              # Returns none if variable is empty
variable_name | format_string('value')     # Returns 'value' if variable is empty
variable_name | format_string(0)           # Returns 0 if variable is empty
variable_name | format_string(True)        # Returns True if variable is empty
variable_name | format_string('null', '"') # Returns 'null' if variable is empty else value enclosed by double quotes.
```

#### format_bool

This filter return specified values in case the value is True or False.

Parameters:

* `when_true`: The value to return if variable equals True. Default: `'true'`.
* `when_false`: The value to return if variable has not been set or equals False. Default: `'false'`.

Usage:

```jinja
variable_name | format_bool                   # Returns 'true' if variable equals True else returns 'false' if variable equals False or is not set
variable_name | format_bool('right')          # Returns 'right' if variable equals True else returns 'false' if variable equals False or is not set
variable_name | format_bool('right', 'wrong') # Returns 'right' if variable equals True else returns 'wrong' if variable equals False or is not set
```
