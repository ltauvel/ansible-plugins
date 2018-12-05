# ansible-plugins

<table cell-spacing="0" cell-padding="0" border="0" style="border-spacing:0; border-collapse:collapse; border:none;"><tr>
    <td width="80px" height="80px"><center><img src="docs/logo.png" width="64px" height="64px"></center></td>
    <td>This repository contains source code for custom Ansible plugins.</td>
</tr></table>

# Setup

Clone the current repository and then run the `install.sh` script. This will launch the `ìnstall.yml` file.
All the python scripts will be installed in `$HOME/.ansible` and will be referenced in the user `$HOME/.ansible.cfg` configuration file.

# Content

## action_plugins

Action plugins act in conjunction with modules to execute the actions required by playbook tasks. They usually execute automatically in the background doing prerequisite work before modules execute.

Check to the following url to get more information:

* https://docs.ansible.com/ansible/2.5/plugins/action.html

## callback_plugins

Callback plugins enable adding new behaviors to Ansible when responding to events. By default, callback plugins control most of the output you see when running the command line programs.

Check to the following url to get more information:

* https://docs.ansible.com/ansible/2.5/dev_guide/developing_plugins.html#callback-plugins
* https://docs.ansible.com/ansible/2.7/plugins/callback.html

## filter_plugins

Filter plugins are used for manipulating data. They are a feature of Jinja2 and are also available in Jinja2 templates used by the template module. As with all plugins, they can be easily extended, but instead of having a file for each one you can have several per file.

Check to the following url to get more information:

* https://docs.ansible.com/ansible/2.5/dev_guide/developing_plugins.html#filter-plugins

## modules

Ansible modules are reusable, standalone scripts that can be used by the Ansible API, or by the ansible or ansible-playbook programs. They return information to ansible by printing a JSON string to stdout before exiting.

Check to the following url to get more information:

* https://docs.ansible.com/ansible/2.5/dev_guide/developing_modules.html