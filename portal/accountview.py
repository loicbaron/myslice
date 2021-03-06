#
import json, os, re, itertools, time
from OpenSSL import crypto
from Crypto.PublicKey import RSA

#
from django.http                        import HttpResponse, HttpResponseRedirect
from django.contrib                     import messages
from django.contrib.auth.decorators     import login_required

#
from manifold.core.query                import Query
from manifoldapi.manifoldapi            import execute_query

from unfold.loginrequired               import LoginRequiredAutoLogoutView
from unfold.page                        import Page    
from ui.topmenu                         import topmenu_items_live, the_user

from portal.actions                     import (
    manifold_update_user, manifold_update_account, manifold_add_account,
    manifold_delete_account, sfa_update_user, sfa_get_user, clear_user_creds, get_myslice_account, get_myslice_platform, get_registry_url, get_jfed_identity )
from portal.account                     import Account, get_expiration

from myslice.settings                   import logger
from myslice.configengine               import ConfigEngine
from myslice.theme                      import ThemeView

# requires login
class AccountView(LoginRequiredAutoLogoutView, ThemeView):
    template_name = "account-view.html"
    def dispatch(self, *args, **kwargs):
        return super(AccountView, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        self.template_name = self.template
        page = Page(self.request)
        metadata = page.get_metadata()
        page.expose_js_metadata()

        page.add_js_files  ( [ "js/jquery.validate.js", "js/my_account.register.js",
                               "js/my_account.edit_profile.js","js/jquery-ui.js" ] )
        page.add_css_files ( [ "css/onelab.css", "css/account_view.css","css/plugin.css" ] )

        # Execute a Query to delegate credentials if necessary
        #sfa_user_query  = Query().get('myslice:user').select('user_hrn').filter_by('user_hrn','==','$user_hrn')
        #sfa_user_result = execute_query(self.request, sfa_user_query)

        user_query  = Query().get('local:user').select('config','email','status')
        user_details = execute_query(self.request, user_query)
        
        # not always found in user_details...
        config={}
        for user_detail in user_details:
            # different significations of user_status
            if user_detail['status'] == 0: 
                user_status = 'Disabled'
            elif user_detail['status'] == 1:
                user_status = 'Validation Pending'
            elif user_detail['status'] == 2:
                user_status = 'Enabled'
            else:
                user_status = 'N/A'
            #email = user_detail['email']
            if user_detail['config']:
                config = json.loads(user_detail['config'])

        platform_query  = Query().get('local:platform').select('platform_id','platform','gateway_type','disabled')
        account_query  = Query().get('local:account').select('user_id','platform_id','auth_type','config')
        platform_details = execute_query(self.request, platform_query)
        account_details = execute_query(self.request, account_query)
       
        # initial assignment needed for users having account.config = {} 
        platform_name = ''
        account_type = ''
        account_usr_hrn = ''
        account_pub_key = ''
        account_priv_key = ''
        account_reference = ''
        my_users = ''
        my_slices = ''
        my_auths = ''
        ref_acc_list = ''
        principal_acc_list = ''
        user_status_list = []
        platform_name_list = []
        platform_name_secondary_list = []
        platform_access_list = []
        platform_no_access_list = []
        total_platform_list = []
        account_type_list = []
        account_type_secondary_list = []
        account_reference_list = []
        delegation_type_list = []
        user_cred_exp_list = []
        slice_list = []
        auth_list = []
        slice_cred_exp_list = []
        auth_cred_exp_list = []
        usr_hrn_list = []
        pub_key_list = []
          
        for platform_detail in platform_details:
            if 'sfa' in platform_detail['gateway_type']:
                total_platform = platform_detail['platform']
                total_platform_list.append(total_platform)
                
            for account_detail in account_details:
                if platform_detail['platform_id'] == account_detail['platform_id']:
                    platform_name = platform_detail['platform']
                    if 'config' in account_detail and account_detail['config'] is not '':
                        account_config = json.loads(account_detail['config'])
                        account_usr_hrn = account_config.get('user_hrn','N/A')
                        account_pub_key = account_config.get('user_public_key','N/A')
                        account_reference = account_config.get ('reference_platform','N/A')
                    # credentials of myslice platform
                    if 'myslice' in platform_detail['platform']:
                        acc_user_cred = account_config.get('delegated_user_credential','N/A')
                        acc_slice_cred = account_config.get('delegated_slice_credentials','N/A')
                        acc_auth_cred = account_config.get('delegated_authority_credentials','N/A')

                        if 'N/A' not in acc_user_cred:
                            exp_date = re.search('<expires>(.*)</expires>', acc_user_cred)
                            if exp_date:
                                user_exp_date = exp_date.group(1)
                                user_cred_exp_list.append(user_exp_date)

                            my_users = [{'cred_exp': t[0]}
                                for t in zip(user_cred_exp_list)]
                       

                        if 'N/A' not in acc_slice_cred:
                            for key, value in acc_slice_cred.iteritems():
                                slice_list.append(key)
                                # get cred_exp date
                                exp_date = re.search('<expires>(.*)</expires>', value)
                                if exp_date:
                                    exp_date = exp_date.group(1)
                                    slice_cred_exp_list.append(exp_date)

                            my_slices = [{'slice_name': t[0], 'cred_exp': t[1]}
                                for t in zip(slice_list, slice_cred_exp_list)]

                        if 'N/A' not in acc_auth_cred:
                            for key, value in acc_auth_cred.iteritems():
                                auth_list.append(key)
                                #get cred_exp date
                                exp_date = re.search('<expires>(.*)</expires>', value)
                                if exp_date:
                                    exp_date = exp_date.group(1)
                                    auth_cred_exp_list.append(exp_date)

                            my_auths = [{'auth_name': t[0], 'cred_exp': t[1]}
                                for t in zip(auth_list, auth_cred_exp_list)]


                    # for reference accounts
                    if 'reference' in account_detail['auth_type']:
                        account_type = 'Reference'
                        delegation = 'N/A'
                        platform_name_secondary_list.append(platform_name)
                        account_type_secondary_list.append(account_type)
                        account_reference_list.append(account_reference)
                        ref_acc_list = [{'platform_name': t[0], 'account_type': t[1], 'account_reference': t[2]} 
                            for t in zip(platform_name_secondary_list, account_type_secondary_list, account_reference_list)]
                       
                    elif 'managed' in account_detail['auth_type']:
                        account_type = 'Principal'
                        delegation = 'Automatic'
                    else:
                        account_type = 'Principal'
                        delegation = 'Manual'
                    # for principal (auth_type=user/managed) accounts
                    if 'reference' not in account_detail['auth_type']:
                        platform_name_list.append(platform_name)
                        account_type_list.append(account_type)
                        delegation_type_list.append(delegation)
                        usr_hrn_list.append(account_usr_hrn)
                        pub_key_list.append(account_pub_key)
                        user_status_list.append(user_status)
                        # combining 5 lists into 1 [to render in the template] 
                        principal_acc_list = [
                            {'platform_name' : pn, 'account_type' : at,
                             'delegation_type' : dt, 'usr_hrn' : uh,
                             'usr_pubkey' : up, 'user_status' : us,} 
                            for pn, at, dt, uh, up, us in zip(platform_name_list, account_type_list, delegation_type_list,
                                         usr_hrn_list, pub_key_list, user_status_list)
                        ]
                    # to hide private key row if it doesn't exist    
                    if 'myslice' in platform_detail['platform']:
                        account_config = json.loads(account_detail['config'])
                        account_priv_key = account_config.get('user_private_key','N/A')
                    if 'sfa' in platform_detail['gateway_type']:
                        platform_access = platform_detail['platform']
                        platform_access_list.append(platform_access)
       
        # Removing the platform which already has access
        for platform in platform_access_list:
            total_platform_list.remove(platform)
        # we could use zip. this one is used if columns have unequal rows 
        platform_list = [{'platform_no_access': t[0]}
            for t in itertools.izip_longest(total_platform_list)]

        # check if the user has creds or not
        if acc_user_cred == {} or acc_user_cred == 'N/A':
            user_cred = 'no_creds'
        else:
            exp_date = get_expiration(acc_user_cred, 'timestamp')
            if exp_date < time.time():
                user_cred = 'creds_expired'
            else:
                user_cred = 'has_creds'

        context = super(AccountView, self).get_context_data(**kwargs)
        context['principal_acc'] = principal_acc_list
        context['ref_acc'] = ref_acc_list
        context['platform_list'] = platform_list
        context['my_users'] = my_users
        context['user_cred'] = user_cred
        context['my_slices'] = my_slices
        context['my_auths'] = my_auths
        context['user_status'] = user_status
        context['person']   = self.request.user
        context['firstname'] = config.get('firstname',"?")
        context['lastname'] = config.get('lastname',"?")
        context['fullname'] = context['firstname'] +' '+ context['lastname']
        context['authority'] = config.get('authority',"Unknown Authority")
        context['user_private_key'] = account_priv_key
        
        # XXX This is repeated in all pages
        # more general variables expected in the template
        context['title'] = 'Platforms connected to MySlice'
        # the menu items on the top
        context['topmenu_items'] = topmenu_items_live('My Account', page)
        # so we can sho who is logged
        context['username'] = the_user(self.request)
        context['theme'] = self.theme
        context['section'] = "User account"
#        context ['firstname'] = config['firstname']

        context['request'] = self.request

        prelude_env = page.prelude_env()
        context.update(prelude_env)
        return context

@login_required
def account_process(request):
    from sfa.trust.credential               import Credential
    from sfa.trust.certificate              import Keypair

    user_query  = Query().get('local:user').select('user_id','email','password','config')
    user_details = execute_query(request, user_query)
    
    account_query  = Query().get('local:account').select('user_id','platform_id','auth_type','config')
    account_details = execute_query(request, account_query)

    platform_query  = Query().get('local:platform').select('platform_id','platform')
    platform_details = execute_query(request, platform_query)
    
    # getting the user_id from the session                                            
    for user_detail in user_details:                                                  
        user_id = user_detail['user_id']                                              
        user_email = user_detail['email']                                             
        try:
            if user_email == request.user.email:                                          
                authorize_query = True                                                    
            else:                                                                         
                logger.error("SECURITY: {} tried to update {}".format(user_email, request.user.email))
                messages.error(request, 'You are not authorized to modify another user.') 
                return HttpResponseRedirect("/portal/account/")                               
        except Exception as e:
            logger.error("exception in account_process {}".format(e))

    for account_detail in account_details:
        for platform_detail in platform_details:
            # Add reference account to the platforms
            if 'add_'+platform_detail['platform'] in request.POST\
               or request.POST['button_value'] == 'add_'+platform_detail['platform']:
                platform_id = platform_detail['platform_id']
                user_params = {'platform_id': platform_id, 'user_id': user_id,
                               'auth_type': "reference",
                               'config': '{"reference_platform": "myslice"}'}
                manifold_add_account(request,user_params)
                messages.info(request, 'Reference Account is added to the selected platform successfully!')
                return HttpResponseRedirect("/portal/account/")

            # Delete reference account from the platforms
            if 'delete_'+platform_detail['platform'] in request.POST\
               or request.POST['button_value'] == 'delete_'+platform_detail['platform']:
                platform_id = platform_detail['platform_id']
                user_params = {'user_id':user_id}
                manifold_delete_account(request,platform_id, user_id, user_params)
                messages.info(request, 'Reference Account is removed from the selected platform')
                return HttpResponseRedirect("/portal/account/")

            if platform_detail['platform_id'] == account_detail['platform_id']:
                if 'myslice' in platform_detail['platform']:
                    account_config = json.loads(account_detail['config'])
                    acc_slice_cred = account_config.get('delegated_slice_credentials','N/A')
                    acc_auth_cred = account_config.get('delegated_authority_credentials','N/A')
                

                    
    
    # adding the slices and corresponding credentials to list
    if 'N/A' not in acc_slice_cred:
        slice_list = []
        slice_cred = [] 
        for key, value in acc_slice_cred.iteritems():
            slice_list.append(key)       
            slice_cred.append(value)
        # special case: download each slice credentials separately 
        for i in range(0, len(slice_list)):
            if 'dl_'+slice_list[i] in request.POST or request.POST['button_value'] == 'dl_'+slice_list[i]:
                slice_detail = "Slice name: " + slice_list[i] +"\nSlice Credentials: \n"+ slice_cred[i]
                response = HttpResponse(slice_detail, content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="slice_credential.txt"'
                return response

    # adding the authority and corresponding credentials to list
    if 'N/A' not in acc_auth_cred:
        auth_list = []
        auth_cred = [] 
        for key, value in acc_auth_cred.iteritems():
            auth_list.append(key)       
            auth_cred.append(value)
        # special case: download each slice credentials separately
        for i in range(0, len(auth_list)):
            if 'dl_'+auth_list[i] in request.POST or request.POST['button_value'] == 'dl_'+auth_list[i]:
                auth_detail = "Authority: " + auth_list[i] +"\nAuthority Credentials: \n"+ auth_cred[i]
                response = HttpResponse(auth_detail, content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="auth_credential.txt"'
                return response

    account_detail = get_myslice_account(request)
             
    if 'submit_name' in request.POST:
        edited_first_name =  request.POST['fname']
        edited_last_name =  request.POST['lname']
        
        config={}
        for user_config in user_details:
            if user_config['config']:
                config = json.loads(user_config['config'])
                config['firstname'] = edited_first_name
                config['lastname'] = edited_last_name
                config['authority'] = config.get('authority','Unknown Authority')
                updated_config = json.dumps(config)
                user_params = {'config': updated_config}
            else: # it's needed if the config is empty 
                user_config['config'] = '{{"firstname":"{}", "lastname":"{}", "authority": "Unknown Authority"}}'\
                                        .format(edited_first_name, edited_last_name)
                user_params = {'config': user_config['config']} 
        # updating config local:user in manifold       
        manifold_update_user(request, request.user.email,user_params)
        # this will be depricated, we will show the success msg in same page
        # Redirect to same page with success message
        messages.success(request, 'Sucess: First Name and Last Name Updated.')
        return HttpResponseRedirect("/portal/account/")       
    
    elif 'submit_pass' in request.POST:
        edited_password = request.POST['password']
        
        for user_pass in user_details:
            user_pass['password'] = edited_password
        #updating password in local:user
        user_params = { 'password' : user_pass['password']}
        manifold_update_user(request, request.user.email, user_params)
#        return HttpResponse('Success: Password Changed!!')
        messages.success(request, 'Success: Password Updated.')
        return HttpResponseRedirect("/portal/account/")

# XXX TODO: Factorize with portal/registrationview.py
# XXX TODO: Factorize with portal/registrationview.py
# XXX TODO: Factorize with portal/joinview.py

    elif 'generate' in request.POST:
        try:
            private = RSA.generate(1024)
            private_key = json.dumps(private.exportKey())
            public  = private.publickey()
            public_key = json.dumps(public.exportKey(format='OpenSSH'))
            # updating manifold local:account table
            account_config = json.loads(account_detail['config'])
            # preserving user_hrn
            user_hrn = account_config.get('user_hrn','N/A')
            keypair = '{"user_public_key":'+ public_key + ', "user_private_key":'+ private_key + ', "user_hrn":"'+ user_hrn + '"}'
            #updated_config = json.dumps(account_config) 
            # updating manifold
            #user_params = { 'config': keypair, 'auth_type':'managed'}
            #manifold_update_account(request, user_id, user_params)
            # updating sfa
            public_key = public_key.replace('"', '');
            user_pub_key = {'keys': public_key}

            sfa_update_user(request, user_hrn, user_pub_key)
            result_sfa_user = sfa_get_user(request, user_hrn, public_key)
            try:
                if 'keys' in result_sfa_user and result_sfa_user['keys'][0] == public_key:
                    # updating manifold
                    updated_config = json.dumps(account_config) 
                    user_params = { 'config': keypair, 'auth_type':'managed'}
                    manifold_update_account(request, user_id, user_params)
                    messages.success(request, 'Sucess: New Keypair Generated! Delegation of your credentials will be automatic.')
                else:
                    raise Exception,"Keys are not matching"
            except Exception as e:
                messages.error(request, 'Error: An error occured during the update of your public key at the Registry, or your public key is not matching the one stored.')
                logger.error("Exception in accountview {}".format(e))
            return HttpResponseRedirect("/portal/account/")
        except Exception as e:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")
                       
    elif 'upload_key' in request.POST:
        try:
            up_file = request.FILES['pubkey']
            file_content =  up_file.read()
            file_name = up_file.name
            file_extension = os.path.splitext(file_name)[1] 
            allowed_extension =  ['.pub','.txt']
            if file_extension in allowed_extension and re.search(r'ssh-rsa',file_content):
                account_config = json.loads(account_detail['config'])
                # preserving user_hrn
                user_hrn = account_config.get('user_hrn','N/A')
                file_content = '{"user_public_key":"'+ file_content + '", "user_hrn":"'+ user_hrn +'"}'
                #file_content = re.sub("\r", "", file_content)
                #file_content = re.sub("\n", "\\n",file_content)
                file_content = ''.join(file_content.split())
                #update manifold local:account table
                user_params = { 'config': file_content, 'auth_type':'user'}
                manifold_update_account(request, user_id, user_params)
                # updating sfa
                user_pub_key = {'keys': file_content}
                sfa_update_user(request, user_hrn, user_pub_key)
                messages.success(request, 'Publickey uploaded! Please delegate your credentials using SFA: http://trac.myslice.info/wiki/DelegatingCredentials')
                return HttpResponseRedirect("/portal/account/")
            else:
                messages.error(request, 'RSA key error: Please upload a valid RSA public key [.txt or .pub].')
                return HttpResponseRedirect("/portal/account/")

        except Exception as e:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")

    elif 'dl_pubkey' in request.POST or request.POST['button_value'] == 'dl_pubkey':
        try:
            account_config = json.loads(account_detail['config'])
            public_key = account_config['user_public_key'] 
            response = HttpResponse(public_key, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="pubkey.txt"'
            return response
        except Exception as e:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")
               
    elif 'dl_pkey' in request.POST or request.POST['button_value'] == 'dl_pkey':
        try:
            account_config = json.loads(account_detail['config'])
            if 'user_private_key' in account_config:
                private_key = account_config['user_private_key']
                response = HttpResponse(private_key, content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="privkey.txt"'
                return response
            else:
                messages.error(request, 'Download error: Private key is not stored in the server')
                return HttpResponseRedirect("/portal/account/")

        except Exception as e:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")
    
    elif 'delete' in request.POST or request.POST['button_value'] == 'delete':
        try:
            account_config = json.loads(account_detail['config'])
            if 'user_private_key' in account_config:
                for key in account_config.keys():
                    if key == 'user_private_key':    
                        del account_config[key]
                    
                updated_config = json.dumps(account_config)
                user_params = { 'config': updated_config, 'auth_type':'user'}
                manifold_update_account(request, user_id, user_params)
                messages.success(request, 'Private Key deleted. You need to delegate credentials manually once it expires.')
                messages.success(request, 'Once your credentials expire, Please delegate manually using SFA: http://trac.myslice.info/wiki/DelegatingCredentials')
                return HttpResponseRedirect("/portal/account/")
            else:
                messages.error(request, 'Delete error: Private key is not stored in the server')
                return HttpResponseRedirect("/portal/account/")
                          
        except Exception as e:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')    
            return HttpResponseRedirect("/portal/account/")
    
    # download identity for jfed
    elif 'dl_identity' in request.POST or request.POST['button_value'] == 'dl_identity':
        try:
            jfed_identity = get_jfed_identity(request)
            if jfed_identity is not None:
                response = HttpResponse(jfed_identity, content_type='text/plain')
                response['Content-Disposition'] = 'attachment; filename="jfed_identity.txt"'
                return response
            else:
                messages.error(request, 'Download error: Private key is not stored in the server')
                return HttpResponseRedirect("/portal/account/")

        except Exception as e:
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
            return HttpResponseRedirect("/portal/account/")

    # Download sfi_config
    elif 'dl_sfi_config' in request.POST or request.POST['button_value'] == 'dl_sfi_config':
        platform_detail = get_myslice_platform(request)
        platform_config = json.loads(platform_detail['config'])
        account_detail = get_myslice_account(request)
        account_config = json.loads(account_detail['config'])

        user_hrn = account_config.get('user_hrn','N/A')
        t_user_hrn = user_hrn.split('.')
        authority_hrn = t_user_hrn[0] + '.' + t_user_hrn[1]
        registry = get_registry_url(request)
        import socket
        hostname = socket.gethostbyaddr(socket.gethostname())[0]
        admin_user = platform_config.get('user','N/A')
        manifold_host = ConfigEngine().manifold_url()
        if 'localhost' in manifold_host:
            manifold_host = manifold_host.replace('localhost',hostname)
        sfi_config  = '[sfi]\n'
        sfi_config += 'auth = '+ authority_hrn +'\n'
        sfi_config += 'user = '+ user_hrn +'\n'
        sfi_config += 'registry = '+ registry +'\n'
        sfi_config += 'sm = http://sfa3.planet-lab.eu:12346/\n\n'
        sfi_config += '[myslice]\n'
        sfi_config += 'backend = '+ manifold_host +'\n'
        sfi_config += 'delegate  = '+ admin_user +'\n'
        sfi_config += 'platform  = myslice\n'
        sfi_config += 'username  = '+ user_email +'\n'
        response = HttpResponse(sfi_config, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="sfi_config"'
        return response

    #clear all creds
    elif 'clear_cred' in request.POST or request.POST['button_value'] == 'clear_cred':
        try:
            result = clear_user_creds(request, user_email)
            if result is not None: 
                messages.success(request, 'All Credentials cleared')
            else:
                messages.error(request, 'Delete error: Credentials are not stored in the server')
        except Exception as e:
            logger.error("Exception in accountview.py in clear_user_creds {}".format(e))
            messages.error(request, 'Account error: You need an account in myslice platform to perform this action')
        return HttpResponseRedirect("/portal/account/")

    # Download delegated_user_cred
    elif 'dl_user_cred' in request.POST or request.POST['button_value'] == 'dl_user_cred':
        if 'delegated_user_credential' in account_config:
            user_cred = account_config['delegated_user_credential']
            response = HttpResponse(user_cred, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="user_cred.txt"'
            return response
        else:
            messages.error(request, 'Download error: User credential is not stored in the server')
            return HttpResponseRedirect("/portal/account/")

    # Download user_cert
    elif 'dl_user_cert' in request.POST or request.POST['button_value'] == 'dl_user_cert':
        if 'user_credential' in account_config:
            user_cred = account_config['user_credential']
            obj_cred = Credential(string=user_cred)
            obj_gid = obj_cred.get_gid_object()
            str_cert = obj_gid.save_to_string()
            response = HttpResponse(str_cert, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="user_certificate.pem"'
            return response

        elif 'delegated_user_credential' in account_config:
            user_cred = account_config['delegated_user_credential']
            obj_cred = Credential(string=user_cred)
            obj_gid = obj_cred.get_gid_object()
            str_cert = obj_gid.save_to_string()
            response = HttpResponse(str_cert, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="user_certificate.pem"'
            return response
        else:
            messages.error(request, 'Download error: User credential is not stored in the server')
            return HttpResponseRedirect("/portal/account/")

    # Download user p12 = private_key + Certificate
    elif 'dl_user_p12' in request.POST or request.POST['button_value'] == 'dl_user_p12':
        if 'user_credential' in account_config and 'user_private_key' in account_config:
            user_cred = account_config['user_credential']
            obj_cred = Credential(string=user_cred)
            obj_gid = obj_cred.get_gid_object()
            str_cert = obj_gid.save_to_string()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, str_cert)

            user_private_key = account_config['user_private_key'].encode('ascii')
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, user_private_key)

            p12 = crypto.PKCS12()
            p12.set_privatekey(pkey)
            p12.set_certificate(cert)       
            pkcs12 = p12.export()

            response = HttpResponse(pkcs12, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="user_pkcs.p12"'
            return response

        elif 'delegated_user_credential' in account_config and 'user_private_key' in account_config:
            user_cred = account_config['delegated_user_credential']
            obj_cred = Credential(string=user_cred)
            obj_gid = obj_cred.get_gid_object()
            str_cert = obj_gid.save_to_string()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, str_cert)

            user_private_key = account_config['user_private_key'].encode('ascii')
            pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, user_private_key)

            p12 = crypto.PKCS12()
            p12.set_privatekey(pkey)
            p12.set_certificate(cert)       
            pkcs12 = p12.export()

            response = HttpResponse(pkcs12, content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename="user_pkcs.p12"'
            return response
        else:
            messages.error(request, 'Download error: User private key or credential is not stored in the server')
            return HttpResponseRedirect("/portal/account/")

    else:
        messages.info(request, 'Under Construction. Please try again later!')
        return HttpResponseRedirect("/portal/account/")


