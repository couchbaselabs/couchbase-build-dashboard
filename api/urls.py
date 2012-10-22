from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import BuildRestHandler, BuildDatabasePopulateRestHandler

build_handler = Resource(BuildRestHandler)
build_populate_handler = Resource(BuildDatabasePopulateRestHandler)

urlpatterns = patterns('',
   url(r'^build/(?P<build_id>.*)$', build_handler),
   url(r'^build$', build_handler),
   url(r'^populate$', build_populate_handler),

)
