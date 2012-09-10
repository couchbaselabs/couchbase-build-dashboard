from django.conf.urls import patterns, url
from django.conf.urls.defaults import *

urlpatterns = patterns('dashboard',
    url(r'^$', 'views.index'),
    (r'^details/$','views.details'),
    (r'^manifest/$','views.manifest'),
    (r'^gitx/$','views.gitx'),
    (r'^populategits/$','views.populate_commits'),
    (r'^populatemanifests/$','views.populate_all_manifests'),
)
