from viewcouchbase.client import CbClient
from piston.handler import BaseHandler
from piston.utils import rc
from django import forms
from couchbase.couchbaseclient import CouchbaseClient
import logging
import json


class BuildRestHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    
    def read(self, request, build_id):
        couchbase = CbClient("localhost", 8091, "Administrator", "password")
        response = []
        allbuilds = couchbase.query(bucket='default', ddoc='builds', 
                     view='metadata', limit=200, params={"startkey":"\"%s\"" % (build_id)})
        for item in allbuilds["rows"]:
            row = item["value"]
            response.append(row)
        couchbase.close()
        return response


    def create(self, request):
        couchbase = CouchbaseClient("http://localhost:8091/pools/default", "default", "")
        if request.content_type:
            data = request.data
            _id = "%s-%s-%s-%s" % (data["package"], data["arch"], data["os"], data["fullversion"])
            _id = _id.encode("ascii", "ignore")
            couchbase.set(_id, 0, 0,json.dumps(data).encode("ascii", "ignore"))
            couchbase.done()
            return {"status":"ok"}
        else:
            return {"status":"failed","data":request.data["os"]}

    def update(self, request, build_id):
        return {"status":"ok"}

    def delete(self, request, build_id):
        return {"status":"ok"}
