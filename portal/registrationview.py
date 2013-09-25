import os.path, re

from django.core.mail           import send_mail

from django.views.generic       import View
from django.template.loader     import render_to_string
from django.shortcuts           import render

from myslice.viewutils          import topmenu_items

from manifold.manifoldapi       import execute_query
from manifold.core.query        import Query

# This is a rough porting from views.py
# the former function-based view is now made a class
# we redefine dispatch as it is simple
# and coincidentally works since we do not need LoginRequiredAutoLogoutView
# a second stab should redefine post and get instead
# also this was not thoroughly tested either, might miss some imports
# to be continued...

class RegistrationView (View):

  def dispatch (self, request):

    errors = []

    #authorities_query = Query.get('authority').filter_by('authority_hrn', 'included', ['ple.inria', 'ple.upmc']).select('name', 'authority_hrn')
    authorities_query = Query.get('authority').select('authority_hrn')
    authorities = execute_query(request, authorities_query)
    authorities = sorted(authorities)

    if request.method == 'POST':
        # We shall use a form here

        #get_email = PendingUser.objects.get(email)
        reg_fname = request.POST.get('firstname', '')
        reg_lname = request.POST.get('lastname', '')
        #reg_aff = request.POST.get('affiliation','')
        reg_auth = request.POST.get('authority_hrn', '')
        reg_email = request.POST.get('email','').lower()
        
        #POST value validation  
        if (re.search(r'^[\w+\s.@+-]+$', reg_fname)==None):
            errors.append('First Name may contain only letters, numbers, spaces and @/./+/-/_ characters.')
            #return HttpResponse("Only Letters, Numbers, - and _ allowd in First Name")
            #return render(request, 'registration_view.html')
        if (re.search(r'^[\w+\s.@+-]+$', reg_lname) == None):
            errors.append('Last Name may contain only letters, numbers, spaces and @/./+/-/_ characters.')
            #return HttpResponse("Only Letters, Numbers, - and _ is allowed in Last name")
            #return render(request, 'registration_view.html')
#        if (re.search(r'^[\w+\s.@+-]+$', reg_aff) == None):
#            errors.append('Affiliation may contain only letters, numbers, spaces and @/./+/-/_ characters.')
            #return HttpResponse("Only Letters, Numbers and _ is allowed in Affiliation")
            #return render(request, 'registration_view.html')
        # XXX validate authority hrn !!
        if PendingUser.objects.filter(email__iexact=reg_email):
            errors.append('Email already registered.Please provide a new email address.')
            #return HttpResponse("Email Already exists")
            #return render(request, 'registration_view.html')
        if 'generate' in request.POST['question']:
            # Generate public and private keys using SFA Library
            from sfa.trust.certificate  import Keypair
            k = Keypair(create=True)
            public_key = k.get_pubkey_string()
            private_key = k.as_pem()
            private_key = ''.join(private_key.split())
            public_key = "ssh-rsa " + public_key
            # Saving to DB
            keypair = '{"user_public_key":"'+ public_key + '", "user_private_key":"'+ private_key + '"}'
#            keypair = re.sub("\r", "", keypair)
#            keypair = re.sub("\n", "\\n", keypair)
#            #keypair = keypair.rstrip('\r\n')
#            keypair = ''.join(keypair.split())
        else:
            up_file = request.FILES['user_public_key']
            file_content =  up_file.read()
            file_name = up_file.name
            file_extension = os.path.splitext(file_name)[1]
            allowed_extension =  ['.pub','.txt']
            if file_extension in allowed_extension and re.search(r'ssh-rsa',file_content):
                keypair = '{"user_public_key":"'+ file_content +'"}'
                keypair = re.sub("\r", "", keypair)
                keypair = re.sub("\n", "\\n",keypair)
                keypair = ''.join(keypair.split())
            else:
                errors.append('Please upload a valid RSA public key [.txt or .pub].')

        #b = PendingUser(first_name=reg_fname, last_name=reg_lname, affiliation=reg_aff, 
        #                email=reg_email, password=request.POST['password'], keypair=keypair)
        #b.save()
        if not errors:
            b = PendingUser(
                first_name=reg_fname, 
                last_name=reg_lname, 
                #affiliation=reg_aff,
                authority_hrn=reg_auth,
                email=reg_email, 
                password=request.POST['password'],
                keypair=keypair
            )
            b.save()

            # Send email
            ctx = {
                first_name   : reg_fname, 
                last_name    : reg_lname, 
                #affiliation  : reg_aff,
                authority_hrn: reg_auth,
                email        : reg_email, 
                keypair      : keypair,
                cc_myself    : True # form.cleaned_data['cc_myself']
            }

            recipients = authority_get_pi_emails(authority_hrn)
            if ctx['cc_myself']:
                recipients.append(ctx['email'])

            msg = render_to_string('user_request_email.txt', ctx)
            send_mail("Onelab New User request for %s submitted"%email, msg, email, recipients)

            return render(request, 'user_register_complete.html')

    return render(request, 'registration_view.html',{
        'topmenu_items': topmenu_items('Register', request),
        'errors': errors,
        'firstname': request.POST.get('firstname', ''),
        'lastname': request.POST.get('lastname', ''),
        #'affiliation': request.POST.get('affiliation', ''),
        'authority_hrn': request.POST.get('authority_hrn', ''),
        'email': request.POST.get('email', ''),
        'password': request.POST.get('password', ''),           
        'authorities': authorities
    })        
