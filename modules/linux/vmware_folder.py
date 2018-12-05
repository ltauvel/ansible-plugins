#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016, Ludovic Tauvel <ludovic.tauvel@gmail.com>
# GitHub : https://github.com/ltauvel/
#
# This file is an Ansible module
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import json
except ImportError:
    import simplejson as json


import atexit
import ssl

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj

def get_folder(root, name):
    obj = None
    for child in root.childEntity:
        if(child.name == name):
            obj = child
            break
    return obj
    
    
def main():
    """
    Simple command-line program for creating host and VM folders in a
    datacenter.
    """

    module = AnsibleModule(
        argument_spec=dict(
            vcenter_hostname=dict(
                type='str'
            ),
            username=dict(
                type='str'
            ),
            password=dict(
                type='str'
            ),
            datacenter=dict(
                type='str'
            ),
            path=dict(
                type='str'
            ),
            state=dict(
                type='str'
            ),
         ),
    )

    vcenter_hostname = module.params['vcenter_hostname']
    username = module.params['username']
    password = module.params['password']
    datacenter = module.params['datacenter']
    path = module.params['path']
    state = module.params['state']

    try:
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(host=vcenter_hostname,
                                                user=username,
                                                pwd=password,
                                                sslContext=context)

        if not service_instance:
            module.fail_json(
            msg="Could not connect to the specified host using specified username and password"
            )

        atexit.register(connect.Disconnect, service_instance)

    except vmodl.MethodFault as e:
        print("Caught vmodl fault : {}".format(e.msg))
        return -1

    content = service_instance.RetrieveContent()
    dc = get_obj(content, [vim.Datacenter], datacenter)

    if state == "present":
        # Replace backslahes with slaches in path
        path=path.replace('\\','/')

        # Loop on each folder begining with the VM root folder
        changed = False
        parentFolder = dc.vmFolder
        for childFolderName in path.split("/"):

            # Handle error with multiple folders separator specified
            if(childFolderName != ''):
            
                # Try to get the current folder
                childFolder = get_folder(parentFolder, childFolderName)
                
                # If the folder does not exists create it
                if(childFolder is None):
                    childFolder = parentFolder.CreateFolder(childFolderName) 
                    changed = True
                    print("Creating child folder : " + childFolderName)

                # assign the curret folder ad the parent for the next loop occurence
                parentFolder = childFolder

        module.exit_json(
            changed=changed,
            name=path,
            Message='The folder path is ready to use.')

    elif state == "exists":
        if (get_obj(content, [vim.Folder], path)):
            exists = True
        else:
            exists = False

        module.exit_json(
            changed=False,
            name=path,
            exists=exists,
            Message='Folder path exists: ' + str(exists))

    else:
        try:
            # Replace backslahes with slaches in path
            path=path.replace('\\','/')

            # Loop on each folder begining with the VM root folder
            changed = False
            folder = dc.vmFolder
            for curFolderName in path.split("/"):

                # Handle error with multiple folders separator specified 
                if(curFolderName != ''):
                
                    # Try to get the current folder
                    folder = get_folder(folder, curFolderName)
                    
            if(folder is not None):
                folder.Destroy()
                module.exit_json(changed=True)
            else:
                module.exit_json(changed=False)
            
            
        except Exception as e:
            module.fail_json(msg=str(e))

# Start program
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
