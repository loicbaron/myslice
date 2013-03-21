from unfold.plugin import Plugin

class Hazelnut (Plugin):

    def __init__ (self, query, **settings):
        Plugin.__init__ (self, **settings)
        self.query=query

    def template_file (self):
        return "hazelnut.html"

    def template_env (self, request):
        env={}
        env.update(self.__dict__)
        # xxx need to retrieve metadata
# $subject_keys = Plugins::get_default_fields($query->subject, $is_unique);
# $fields = Plugins::metadata_get_fields($query->subject);
# for now I am hard-coding the ones from haze.py
        env['subject_fields']=[ 'hostname', 'hrn' ]
        return env

    def requirements (self):
        reqs = {
            'js_files' : [ "js/hazelnut.js", 
                           "js/manifold.js", "js/manifold-query.js",
                           "js/dataTables.js", "js/with-datatables.js",
                           "js/spin.presets.js", "js/spin.min.js", "js/jquery.spin.js", 
                           "js/unfold-helper.js",
                           ] ,
            'css_files': [ "css/hazelnut.css" ],
            }
        return reqs

    # the list of things passed to the js plugin
    def json_settings_list (self): return ['plugin_uuid','query_uuid']
