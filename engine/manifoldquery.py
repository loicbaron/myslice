import json

# xxx php has uniqid, need to find a module for that
counter=1
def uniqid (): global counter; counter += 1; return counter

class ManifoldQuery:

    def __init__ (self, action=None, method=None, timestamp='now',
                  filters=[], params=[], fields=[],
                  sort=None, limit=None, offset=None,
                  ):
        self.uuid=uniqid()
        # settable
        self.action=action
        self.method=method
        self.timestamp=timestamp
        self.filters=filters
        self.params=params
        self.fields=fields
        self.sort=sort
        self.limit=limit
        self.offset=offset
        # internal data
        self.analyzed_query=None
        self.subqueries = {}

    def to_json (self):
        uuid=self.uuid
        a=self.action
        m=self.method
        t=self.timestamp
        f=json.dumps (self.filters)
        p=json.dumps (self.params)
        c=json.dumps (self.fields)
        # xxx unique can be removed, but for now we pad the js structure
        unique=0

        aq = self.analyzed_query.to_json() if self.analyzed_query else 'null'
        # subqueries is a dictionary method:query
        if not self.subqueries: 
            sq="{}"
        else:
            sq=", ".join ( [ "'%s':%s" % (method, subquery.to_json())
                      for (method, subquery) in self.subqueries.iteritems()])
            sq="{%s}"%sq
        
        return """ new Query('%(a)s', '%(m)s', '%(t)s', %(f)s, %(p)s, %(c)s, %(unique)s, '%(uuid)s', %(aq)s, %(sq)s)"""%locals()
    
    # 4amine
    # xxx
    # this should build an object from a dict as received from javascript
    # to see an example just look at the server's output
    # incoming POST <QueryDict: {u'query[method]': [u'slice'], u'query[fields][]': [u'slice_hrn'], u'query[ts]': [u'latest'], u'query[action]': [u'get']}>
    def fill_from_dict (self, d):
        # mandatory...
        self.action=d['query[action]']
        self.method=d['query[method]']
        self.fields=[d['query[fields][]']]
        self.timestamp=d['query[ts]'] 
        #self.filters=d['filters']
        #self.params=d['params']
