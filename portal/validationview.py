# -*- coding: utf-8 -*-
#
# portal/views.py: views for the portal application
# This file is part of the Manifold project.
#
# Authors:
#   Jordan Augé <jordan.auge@lip6.fr>
#   Mohammed Yasin Rahman <mohammed-yasin.rahman@lip6.fr>
#   Loic Baron <loic.baron@lip6.fr>
# Copyright 2013, UPMC Sorbonne Universités / LIP6
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# 
# You should have received a copy of the GNU General Public License along with
# this program; see the file COPYING.  If not, write to the Free Software
# Foundation, 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import json

from django.http                import HttpResponseRedirect, HttpResponse
from django.shortcuts           import render
from django.template.loader     import render_to_string

from unfold.loginrequired       import FreeAccessView
from ui.topmenu                 import topmenu_items_live, the_user

from portal.event               import Event
# presview is put in observation for now
#from plugins.pres_view          import PresView
from plugins.raw                import Raw

# these seem totally unused for now
#from portal.util                import RegistrationView, ActivationView

from portal.models              import PendingUser, PendingSlice
from portal.actions             import get_request_by_authority
from manifold.manifoldapi       import execute_query
from manifold.core.query        import Query
from unfold.page                import Page

class ValidatePendingView(FreeAccessView):
    template_name = "validate_pending.html"

    def get_context_data(self, **kwargs):
        # We might have slices on different registries with different user accounts 
        # We note that this portal could be specific to a given registry, to which we register users, but i'm not sure that simplifies things
        # Different registries mean different identities, unless we identify via SFA HRN or have associated the user email to a single hrn

        #messages.info(self.request, 'You have logged in')
        page = Page(self.request)

        ctx_my_authorities = {}
        ctx_delegation_authorities = {}


        # The user need to be logged in
        if the_user(self.request):
            # Who can a PI validate:
            # His own authorities + those he has credentials for.
            # In MySlice we need to look at credentials also.
            

            # XXX This will have to be asynchroneous. Need to implement barriers,
            # for now it will be sufficient to have it working statically

            # get user_id to later on query accounts
            # XXX Having real query plan on local tables would simplify all this
            # XXX $user_email is still not available for local tables
            #user_query = Query().get('local:user').filter_by('email', '==', '$user_email').select('user_id')
            user_query = Query().get('local:user').filter_by('email', '==', the_user(self.request)).select('user_id')
            user, = execute_query(self.request, user_query)
            user_id = user['user_id']

            # Query manifold to learn about available SFA platforms for more information
            # In general we will at least have the portal
            # For now we are considering all registries
            all_authorities = []
            platform_ids = []
            sfa_platforms_query = Query().get('local:platform').filter_by('gateway_type', '==', 'sfa').select('platform_id', 'platform', 'auth_type')
            sfa_platforms = execute_query(self.request, sfa_platforms_query)
            for sfa_platform in sfa_platforms:
                print "SFA PLATFORM > ", sfa_platform['platform']
                if not 'auth_type' in sfa_platform:
                    continue
                auth = sfa_platform['auth_type']
                if not auth in all_authorities:
                    all_authorities.append(auth)
                platform_ids.append(sfa_platform['platform_id'])

            print "W: Hardcoding platform myslice"
            # There has been a tweak on how new platforms are referencing a
            # so-called 'myslice' platform for storing authentication tokens.
            # XXX This has to be removed in final versions.
            myslice_platforms_query = Query().get('local:platform').filter_by('platform', '==', 'myslice').select('platform_id')
            myslice_platforms = execute_query(self.request, myslice_platforms_query)
            if myslice_platforms:
                myslice_platform, = myslice_platforms
                platform_ids.append(myslice_platform['platform_id'])

            # We can check on which the user has authoritity credentials = PI rights
            credential_authorities = set()
            credential_authorities_expired = set()

            # User account on these registries
            user_accounts_query = Query.get('local:account').filter_by('user_id', '==', user_id).filter_by('platform_id', 'included', platform_ids).select('auth_type', 'config')
            user_accounts = execute_query(self.request, user_accounts_query)
            #print "=" * 80
            #print user_accounts
            #print "=" * 80
            for user_account in user_accounts:

                print "USER ACCOUNT", user_account
                if user_account['auth_type'] == 'reference':
                    continue # we hardcoded the myslice platform...

                config = json.loads(user_account['config'])
                creds = []
                print "CONFIG KEYS", config.keys()
                if 'authority_credentials' in config:
                    print "***", config['authority_credentials'].keys()
                    for authority_hrn, credential in config['authority_credentials'].items():
                        #if credential is not expired:
                        credential_authorities.add(authority_hrn)
                        #else
                        #    credential_authorities_expired.add(authority_hrn)
                if 'delegated_authority_credentials' in config:
                    print "***", config['delegated_authority_credentials'].keys()
                    for authority_hrn, credential in config['delegated_authority_credentials'].items():
                        #if credential is not expired:
                        credential_authorities.add(authority_hrn)
                        #else
                        #    credential_authorities_expired.add(authority_hrn)

            print 'credential_authorities =', credential_authorities
            print 'credential_authorities_expired =', credential_authorities_expired

            # ** Where am I a PI **
            # For this we need to ask SFA (of all authorities) = PI function
            pi_authorities_query = Query.get('user').filter_by('user_hrn', '==', '$user_hrn').select('pi_authorities')
            pi_authorities_tmp = execute_query(self.request, pi_authorities_query)
            pi_authorities = set()
            for pa in pi_authorities_tmp:
                pi_authorities |= set(pa['pi_authorities'])

            print "pi_authorities =", pi_authorities
            
            # My authorities + I have a credential
            pi_credential_authorities = pi_authorities & credential_authorities
            pi_no_credential_authorities = pi_authorities - credential_authorities - credential_authorities_expired
            pi_expired_credential_authorities = pi_authorities & credential_authorities_expired
            # Authorities I've been delegated PI rights
            pi_delegation_credential_authorities = credential_authorities - pi_authorities
            pi_delegation_expired_authorities = credential_authorities_expired - pi_authorities

            print "pi_credential_authorities =", pi_credential_authorities
            print "pi_no_credential_authorities =", pi_no_credential_authorities
            print "pi_expired_credential_authorities =", pi_expired_credential_authorities
            print "pi_delegation_credential_authorities = ", pi_delegation_credential_authorities
            print "pi_delegation_expired_authorities = ", pi_delegation_expired_authorities

            # Summary intermediary
            pi_my_authorities = pi_credential_authorities | pi_no_credential_authorities | pi_expired_credential_authorities
            pi_delegation_authorities = pi_delegation_credential_authorities | pi_delegation_expired_authorities

            print "--"
            print "pi_my_authorities = ", pi_my_authorities
            print "pi_delegation_authorities = ", pi_delegation_authorities

            # Summary all
            queried_pending_authorities = pi_my_authorities | pi_delegation_authorities
            print "----"
            print "queried_pending_authorities = ", queried_pending_authorities

            requests = get_request_by_authority(queried_pending_authorities)
            print "requests = ", requests
            for request in requests:
                auth_hrn = request['authority_hrn']

                if auth_hrn in pi_my_authorities:
                    dest = ctx_my_authorities

                    # define the css class
                    if auth_hrn in pi_credential_authorities:
                        request['allowed'] = 'allowed'
                    elif auth_hrn in pi_expired_credential_authorities:
                        request['allowed'] = 'expired'
                    else: # pi_no_credential_authorities
                        request['allowed'] = 'denied'

                elif auth_hrn in pi_delegation_authorities:
                    dest = ctx_delegation_authorities

                    if auth_hrn in pi_delegation_credential_authorities:
                        request['allowed'] = 'allowed'
                    else: # pi_delegation_expired_authorities
                        request['allowed'] = 'expired'

                else:
                    continue

                if not auth_hrn in dest:
                    dest[auth_hrn] = []
                dest[auth_hrn].append(request) 
        
        context = super(ValidatePendingView, self).get_context_data(**kwargs)
        context['my_authorities']   = ctx_my_authorities
        context['delegation_authorities'] = ctx_delegation_authorities

        # XXX This is repeated in all pages
        # more general variables expected in the template
        context['title'] = 'Test view that combines various plugins'
        # the menu items on the top
        context['topmenu_items'] = topmenu_items_live('Validation', page) 
        # so we can sho who is logged
        context['username'] = the_user(self.request) 

        # XXX We need to prepare the page for queries
        #context.update(page.prelude_env())

        return context