#!/usr/bin/python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import ldap

from ansible.module_utils.basic import *

def connect(address, username, password):
    result = None

    # Checking the address parameter format
    ldapurl = re.compile("^ldap://")
    if not(ldapurl.match(address)):
        address = "ldap://" + address
    
    # Sometime the python-ldap response that the server cannot be contacted
    # So trying to loop 3 times until the request response is correct
    retry = 1
    while retry <= 3:
        try:
        
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT,0)
            result = ldap.initialize(address)
            result.set_option(ldap.OPT_REFERRALS, 0)
            result.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            #result.set_option(ldap.OPT_NETWORK_TIMEOUT, 10.0)

            # Any errors will throw an ldap.LDAPError exception 
            # or related exception so you can ignore the result
            result.simple_bind(username, password)
        
            break
        except ldap.LDAPError:
            retry += 1
            result = None
            time.sleep(1) 
    
    return result

def search(cnx, basedn, filter):
    result = []

    # Sometime the python-ldap response that the server is busy
    # So trying to loop 10 times until the request response is correct
    retry = 1
    while retry <= 10:
        try:
            entries = cnx.search_s(basedn, ldap.SCOPE_SUBTREE, filter, None)
            break
        except ldap.LDAPError, e:
            retry += 1
            time.sleep(1)
    
    # Generate a filtered resut list because some None entries
    # may be returned by the python-ldap module
    for entry in entries:
        if(entry[0] is not None):
            result.append(entry)
    
    return result
    
    
def main():
    try:
        # Arguments definition and parsing
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        module = AnsibleModule(
            argument_spec=dict(
                servers     = dict(type='list', required=True),
                username    = dict(type='str', required=True),
                password    = dict(type='str', required=True),
                basedn      = dict(type='str', required=True),
                accountname = dict(type='str', required=True),
                oupath      = dict(type='str', required=False),
                state       = dict(type='str', required=False, default='present', choices=['present', 'absent']),
                force       = dict(type='bool', required=False, default=False, choices=BOOLEANS),
             ),
        )

        servers = module.params['servers']
        username = module.params['username']
        password = module.params['password']
        basedn = module.params['basedn']
        accountname = module.params['accountname']
        oupath = module.params['oupath']
        force = module.params['force']
        state = module.params['state']


        # Connecting to LDAP server
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        for server in servers:
            print "Trying to connect to server " + server
            cnx = connect(server, username, password)
            
            if cnx:
                print "Connection succeed"
                break
            else:
                print "Unable to connect"

        # Handling ldap operations
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
        if cnx:            
            if(state == "absent"):
                changed = False
                entries = search(cnx, basedn, "cn=" + accountname)
                
                # Break the execution if more than one valid entry has been found
                # and the force parameter has been set to False to avoid massive
                # destruction errors
                if(len(entries) > 1 and not(force)):
                    module.fail_json(msg="Unable to delete " + str(len(entries)) + " entries at once")
                    print 
                else:
                    for entry in entries:
                        changed = True
                        cnx.delete(entry[0])
                            
                    module.exit_json(
                        changed=changed,
                        entries=entries,
                        msg=str(len(entries)) + ' entries has been removed')

            elif(state == "present"):
                module.fail_json(msg="State has not ben implement yet")
                
        else:
            module.fail_json(msg="Unable to connect to any of the specified ldap server")
            

    except Exception as e:
        module.fail_json(msg=str(e))          

# Start program
if __name__ == "__main__":
    main()
 