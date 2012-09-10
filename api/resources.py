from tastypie.resources import BuildRestResource

class BuildRestResource(ModelResource):
    allowed_methods = ['get']

    def read(self, request, fullversion):
        return {"status":"ok"}
#        couchbase = CbClient("localhost", 8091, "Administrator", "password")
#        response = []
#        allbuilds = couchbase.query(bucket='default', ddoc='builds',
#                     view='metadata', limit=200, params={"startkey":"\"%s\"" % (fullversion)})
#        for item in allbuilds["rows"]:
#            row = item["value"]
#            response.append(row)
#        couchbase.close()
#        return {"status":"ok"} 
#        return response
    
    def create(self, request, fullversion):
        return {"status":"ok"}

    def update(self, request, build_id):
        return {"status":"ok"}

    def delete(self, request, build_id):
        return {"status":"ok"}
   
