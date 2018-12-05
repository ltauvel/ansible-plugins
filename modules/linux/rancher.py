#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import requests
import json 
import time

from ansible.module_utils.basic import *

   
def _checkParamSpec(parameterspec, parameter, ansible):
    
    # If the parameter value is undefined
    # Never fail because required undefined values are already
    # handled by ansible libraries
    if parameter:
    
        # Add missing parameter to the parameter list
        for key in parameterspec:
            if key not in ['type', 'required', 'default', 'choices', 'mutually_exclusive']:
                if key not in parameter:
                    parameter[key] = '' 
        
        # Check each parameter
        for key in parameterspec:
            if key not in ['type', 'required', 'default', 'choices']:
                subparameterspec = parameterspec[key]           
                
                if 'default' in subparameterspec:
                    if not(parameter[key]):
                        parameter[key] = subparameterspec['default']

                if 'required' in subparameterspec:
                    if subparameterspec['required'] and not(parameter[key]):
                        ansible.fail_json(msg="Missing required field " + key) 
                        
                if 'choices' in subparameterspec:
                    if parameter[key]  and parameter[key] not in subparameterspec['choices']:
                        ansible.fail_json(msg="Invalid value for field " + key + ". Allowed values are " + str(subparameterspec['choices']))  

        # Check for mutually exclusive parameters 
        if 'mutually_exclusive' in parameterspec:
            match = False
            for key in parameterspec['mutually_exclusive']:
                if parameter[key]:
                    if match:   
                        ansible.fail_json(msg="The fields " + str(parameterspec['mutually_exclusive']) + " are mutually exclusives")  
                    else:
                        match = True 
 
    return parameter
    
def _getProjects(url, project_id = None, project_name = None, project_index = None):
    url = url + "v1/projects/"
    
    if project_id:
        url = url + project_id
        result = requests.get(url).json()
    else:
        result = requests.get(url).json()
        if project_name:
            found = False
            for item in result['data']:
                if item['name'] == project_name:
                    url = url + item['id']
                    result = item
                    found = True
                    break
            if not(found):
                result = None
        elif project_index:
            result = result['data'][project_index]
            url = url + result['data'][project_index]['id']
                    
    return {'url': url, 'response': result}

def _getHosts(url, host_id = None, host_name = None):
    url = url + "/hosts/"
    
    if host_id:
        url = url + host_id
        result = requests.get(url).json()
    else:
        result = requests.get(url).json()
        if host_name:
            found = False
            for item in result['data']:
                if item['hostname'] == host_name:
                    url = url + item['id']
                    result = item
                    found = True
                    break
            if not(found):
                result = None
                    
    return {'url': url, 'response': result}
    
def main():
       
    # Arguments definition and parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    project_spec=dict(type='dict', required=False,
        project_id          = dict(type='str', required=False),
        project_name        = dict(type='str', required=False),
        project_type        = dict(type='str', default='account', required=False, choices=['account']),
        action              = dict(type='str', default='list', choices=['list', 'add', 'remove']),
        mutually_exclusive  = ['project_id', 'project_name'],
    )
    host_spec=dict(type='dict', required=False,
        project_id          = dict(type='str', required=False),
        project_name        = dict(type='str', required=False),
        host_name           = dict(type='str', required=False),
        action              = dict(type='str', default='list', choices=['list', 'unregister']),
        mutually_exclusive  = ['project_id', 'project_name'],
    )
    registration_spec=dict(type='dict', required=False,
        project_id          = dict(type='str', required=False),
        project_name        = dict(type='str', required=False),
        token_url           = dict(type='str', required=False),
        action              = dict(type='str', default='list', choices=['create', 'remove']),
        mutually_exclusive  = ['project_id', 'project_name'],
    )
    
    module = AnsibleModule(
        argument_spec=dict(
            api_address  = dict(type='str', required=False, default="localhost"),
            api_port     = dict(type='int', required=False, default=8080),
            api_token    = dict(type='str', required=False),
            project      = project_spec,
            host         = host_spec,
            registration = registration_spec,
        ),
        mutually_exclusive=[['project', 'host', 'registration']],
    )
    
    try: 
    
        api_address = module.params['api_address']
        api_port = module.params['api_port']
        project = _checkParamSpec(project_spec, module.params['project'], module)
        host = _checkParamSpec(host_spec, module.params['host'], module)
        registration = _checkParamSpec(registration_spec, module.params['registration'], module)
        
        # Initialize global variables
        url = "http://" + api_address + ":" + str(api_port) + "/"
        changed = False
        msg = ""
        result = {}
        
        #
        # PROJECTS ACTIONS
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        if project:
        
            # Initialise project variables
            project_id = project['project_id']
            project_name = project['project_name']
            project_type = project['project_type']
            action = project['action']
            
            # Try to get a response from rancher to list one or more
            # project according to the specified parameters
            result = _getProjects(url, project_id, project_name)
            
            # If ADD has been specified and a project with the same name
            # has not been found then create the new one else ignore
            if action == 'add' and result['response'] is None:
                result = requests.post(
                    result['url'],
                    data=json.dumps({'baseType': project_type, 'name': project_name}),
                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                    ).json()
                changed = True
                
            # If REMOVE has been specified and a project with the same name
            # has been found then delete the project else ignore
            elif action == 'remove' and result['response']:
                result = requests.delete(
                    result['url'],
                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                    ).json()
                changed = True
                
        #
        # HOSTS ACTIONS
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        elif host:
        
            # Initialise project variables
            project_id = host['project_id']
            project_name = host['project_name']
            host_name = host['host_name']
            action = host['action']
            
            # Try to get a response from rancher to list one or more
            # project according to the specified parameters
            if project_id or project_name:
                result = _getProjects(url, project_id, project_name)
            else:
                result = _getProjects(url, "", "Default")
                if not(result['response']):
                    result = _getProjects(url, "", "", 0)
            
            if result['response']:                    
                
                # Try to get a response from rancher to list one or more
                # host according to the specified parameters
                result = _getHosts(result['url'], "", host_name)  
                    
                # If UNREGISTER has been specified and a host with the same name
                # has been found then unregister the host else ignore
                if action == 'unregister': 
                    
                    if result['response']:
                        result = requests.delete(
                            result['url'],
                            headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                            ).json()
                        changed = True
            else:
                module.fail_json(msg='Unable to find a project')

        #
        # REGISTRATION TOKEN ACTION
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        elif registration:
        
            # Initialise project variables
            project_id = registration['project_id']
            project_name = registration['project_name']
            token_url = registration['token_url']
            action = registration['action']
            
            # Try to get a response from rancher to list one or more
            # project according to the specified parameters
            if project_id or project_name:
                result = _getProjects(url, project_id, project_name)
            else:
                result = _getProjects(url, "", "Default")
                if not(result['response']):
                    result = _getProjects(url, "", "", 0)
            
            if result['response']:
            
                # If REGISTER has been specified and a project 
                # has been found then register the host else ignore
                if action == 'create':
                    result = requests.post(url + 'v1/registrationtokens?projectId=' + result['response']['id']).json()
                    
                    # Sleep for 2 seconds between token creation and query
                    time.sleep( 2 )
                    
                    result = requests.get(result['links']['self']).json()
                    changed = True
                    

                # If UNREGISTER has been specified and a host with the same name
                # has been found then unregister the host else ignore
                elif action == 'remove':
                    result = requests.post(
                        token_url + "/?action=deactivate",
                        headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                        ).json()
                        
                    # Sleep for 2 seconds between deactivation and removal
                    time.sleep( 2 )
                    
                    result = requests.post(
                        token_url + "/?action=remove",
                        headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                        ).json()
                    changed = True
            else:
                module.fail_json(msg='Unable to find a project')

            # ############# REMOVE HOST ######################
            # curl -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' -d '{}' 'http://10.155.20.82:8080/v1/hosts/1h14/?action=deactivate'
            # curl -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' -d '{}' 'http://10.155.20.82:8080/v1/hosts/1h14/?action=remove'

            # ############## REMOVE PROJECT #######################
            # curl -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' -d '{}' 'http://10.155.20.81:8080/v1/projects/1a2128/?action=deactivate'
            # curl -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' -d '{}' 'http://10.155.20.82:8080/v1/projects/1a2128/?action=remove'
            # curl -X POST -H 'Accept: application/json' -H 'Content-Type: application/json' -d '{}' 'http://10.155.20.82:8080/v1/projects/1a2128/?action=purge' 
            
        #
        # RETURN VALUE
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #   
        if 'response' in result:
            module.exit_json(
                changed=changed,
                json=result['response'],
                msg=msg) 
        else:
            module.exit_json(
                changed=changed,
                json=result,
                msg=msg)   
        
    except Exception as e:
        module.fail_json(msg=str(e))          

# Start program
if __name__ == "__main__":
    main()
 