# Create your views here.
from copy import deepcopy

from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

lorem="""
Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat. Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Nam liber tempor cum soluta nobis eleifend option congue nihil imperdiet doming id quod <code>mazim placerat</code> facer possim assum. Typi non habent claritatem insitam; est usus legentis in iis qui facit eorum claritatem. Investigationes demonstraverunt lectores legere me lius quod ii legunt saepius. Claritas est etiam processus dynamicus, qui sequitur mutationem consuetudium lectorum. Mirum est notare quam littera gothica, quam nunc putamus parum claram, anteposuerit litterarum formas humanitatis per seacula quarta decima et quinta decima. Eodem modo typi, qui nunc nobis videntur parum clari, fiant sollemnes in futurum.
"""

standard_menu_items = [ { 'label':'Slice view',  'href': '/slice/'},
                        { 'label':'Scroll view', 'href': '/scroll/'},
                        { 'label':'Tab view', 'href': '/tab/'},
                        { 'label':'Mini plugin', 'href': '/plugin/'},
                        ]

login_out_items = { False: { 'label':'Login', 'href':'/login/'},
                    True:  { 'label':'Logout', 'href':'/logout/'}}

def menu_items (current,request=None):
    result=deepcopy(standard_menu_items)
    for d in result:
        if d['label'].lower().find(current)>=0: d['active']=True
    if not request: return result
    has_user=request.user.is_authenticated()
    result.append (login_out_items [ has_user] )
    return result

hard_wired_slice_names = []
for site in [ 'inria', 'upmc' , 'ibbt' ]:
    for slice in [ 'foo', 'bar', 'tutu', 'test', 'omf', 'heartbeat' ]:
        hard_wired_slice_names.append ("ple.%s.%s"%(site,slice))

def the_user (request):
    "This code below is broken"
    return 'user-xxx-name'
    if not request.user.is_authenticated (): return ''
    else: return request.user.username

@login_required
def fake_slice_view (request, name=None):
    title='Fake Slice Page'
    if name: title += " for slice %s"%name
    result=render_to_response ('view-slice.html',
                               {'name':name,
                                'title':title,
                                'menu_items' : menu_items('slice',request),
                                'username':the_user (request),
                                'slices': hard_wired_slice_names,
                                'content_main' : lorem,
                                },
                               context_instance=RequestContext(request))

    return result

@login_required
def tab_view (request):
    return render_to_response ('view-tab.html',
                               {'title':'Page for playing with Tabs',
                                'menu_items': menu_items('tab',request),
                                'username':the_user (request),
                                'lorem': lorem,                                
                                },
                               context_instance=RequestContext(request))

@login_required
def scroll_view (request):
    return render_to_response ('view-scroll.html',
                               {'title':'Toy page for scrolling',
                                'menu_items': menu_items('scroll',request),
                                'username':the_user (request),
                                'lorem':lorem,
                                },
                               context_instance=RequestContext(request))
