# Create your views here.

from django.core.context_processors import csrf
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response

from plugins.verticallayout import VerticalLayout
from plugins.tabs import Tabs
from plugins.simplelist import SimpleList
from plugins.slicelist import SliceList
from plugins.raw import Raw

from myslice.viewutils import topmenu_items, the_user
from myslice.viewutils import hard_wired_slice_names, hard_wired_list, lorem_p, lorem

def test_plugin_view (request):
    
    # variables that will get passed to this template
    template_env = {}
    
    main_plugin = \
        VerticalLayout ( title='title for the vertical layout',name='vertical1',
        sons = [ SimpleList (title='SimpleList and dataTables',
                             name='simplelist1',
                             list=hard_wired_list, 
                             header='Hard wired', 
                             foo='the value for foo',
                             with_datatables=True,
                             toggled=False),
                 Tabs (title='Sample Tabs',name='tabs1',
                       active='raw1',
                       sons = [ Raw (title='a raw plugin',name='raw1',
                                     togglable=False,
                                     html= 3*lorem_p),
                                SliceList(title='a slice list',name='slicelist-main',
                                          togglable=False,
                                          list=hard_wired_slice_names),
                                Raw (title='raw title',name='raw2',
                                     togglable=False,html=lorem) ]),
                 SimpleList (title='SimpleList with slice names', 
                             name='simplelist2',
                             list=hard_wired_slice_names,
                             ) ] )
    # define 'content_main' to the template engine
    template_env [ 'content_main' ] = main_plugin.render(request)

    ##########
    # lacks a/href to /slice/%s
    related_plugin = SliceList (title='SliceList plugin',name='slicelist1',
                                with_datatables='yes', 
                                list=hard_wired_slice_names, 
                                header='Slices')
    # likewise but on the side view
    template_env [ 'content_related' ] = related_plugin.render (request)

    # more general variables expected in the template
    template_env [ 'title' ] = 'Test Plugin View' 
    template_env [ 'topmenu_items' ] = topmenu_items('plugin', request) 
    template_env [ 'username' ] = the_user (request) 

    # request.plugin_prelude holds a summary of the requirements() for all plugins
    # define {js,css}_{files,chunks}
    prelude_env = request.plugin_prelude.template_env()
    template_env.update(prelude_env)

    return render_to_response ('view-plugin.html',template_env,
                               context_instance=RequestContext(request))
                               
