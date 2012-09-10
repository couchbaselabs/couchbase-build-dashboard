from django import http
from django.conf import settings
from django.core import urlresolvers
from django.shortcuts import get_object_or_404, redirect
from django.utils import simplejson
from django.utils.encoding import force_unicode
from viewcouchbase.client import CbClient

class RESTResource(object):
    """
    Dispatches based on HTTP method.
    """
    # Possible methods; subclasses could override this.
    methods = ['GET', 'POST', 'PUT', 'DELETE']
    
    def __call__(self, request, *args, **kwargs):
        callback = getattr(self, request.method, None)
        if callback:
            return callback(request, *args, **kwargs)
        else:
            allowed_methods = [m for m in self.methods if hasattr(self, m)]
            return http.HttpResponseNotAllowed(allowed_methods)

class BuildResource(RestResource):
    """
    Base class for all build resources providing information about builds
    """
    def GET(self, request):
        """
        /api/builds
        """
        request_json = json.loads(request.raw_post_data)
        builds = self._fetch_builds(request["version"])
        return JSONResponse(builds)

    def _fetch_builds(self, fullversion):
        couchbase = CbClient("localhost, 8091, "Administrator", "password")
        response = []
        all_builds = couchbase.query(bucket='default', ddoc='builds', 
                     view='metadata', limit=200, params={"startkey":"\"%s\"" % (fullversion)})
        for item in allbuilds["rows"]:
            row = item["value"]
            response.append(row)
        couchbase.close()
        return response 

    def PUT(self, build):
        build = self.parse(json.loads(request.raw_post_data))
        if not build:
            return http.HttpResponseBadRequest()
        return JSONResponse(self.format( 
        author = self.parse(simplejson.loads(request.raw_post_data))
        if not author:
            return http.HttpResponseBadRequest()
        author.id = id
        author.save()
        return JSONResponse({"status":"ok"})
        

class JSONResponse(http.HttpResponse):
    def __init__(self, data):
        indent = 2 if settings.DEBUG else None
        mime = ("text/javascript" if settings.DEBUG 
                                  else "application/json")
        super(JSONResponse, self).__init__(
            content = simplejson.dumps(data, indent=indent),
            mimetype = mime,
        )
