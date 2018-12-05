# filter_plugins

## Purpose

Filter plugins are used for manipulating data. They are a feature of Jinja2 and are also available in Jinja2 templates used by the template module. As with all plugins, they can be easily extended, but instead of having a file for each one you can have several per file.

Check to the following url to get more information:

* https://docs.ansible.com/ansible/2.5/dev_guide/developing_plugins.html#filter-plugins

## Plugins list

### skippy_yaml

This plugin combine both of the official [yaml](https://docs.ansible.com/ansible/2.7/plugins/callback/yaml.html) and [skippy](https://docs.ansible.com/ansible/2.7/plugins/callback/skippy.html) features.