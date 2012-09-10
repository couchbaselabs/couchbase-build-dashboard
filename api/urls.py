from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import BuildRestHandler

build_handler = Resource(BuildRestHandler)

urlpatterns = patterns('',
   url(r'^build/(?P<build_id>.*)$', build_handler),
   url(r'^build$', build_handler),
)
