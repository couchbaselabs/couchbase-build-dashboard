import json
import logging
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import loader
from django.template.context import Context, RequestContext
from viewcouchbase.client import CbClient
from couchbase.couchbaseclient import CouchbaseClient
from git import *
import memcache
from gitpopulate import GitPopulate
import sys
from populatemanifest import ManifestPopulate

import django_tables2 as tables


class DataHelper(object):
	
	@staticmethod
	def multikeysort(items, columns):
	    from operator import itemgetter
	    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]  
	    def comparer(left, right):
	        for fn, mult in comparers:
	            result = cmp(fn(left), fn(right))
	            if result:
	                return mult * result
	        else:
	            return 0
	    return sorted(items, cmp=comparer)

class ArtifactsTable(tables.Table):
    name = tables.Column(orderable=True)
    url = tables.Column()
    arch = tables.Column()
    os = tables.Column()
    version = tables.Column()
    fullversion = tables.Column()


# mac,linux,windows
def index(request):
    t = loader.get_template('../templates/dashboard/index.html')
    #how many versions
    versions = {"2.0.0": "", "1.8.1": ""}
    versions["2.0.0"] = {
        "mac": "Mac OSX", "windows": "Windows Server 64-bit/32-bit", "centos": "Centos 32-bit/64-bit",
        "ubuntu": "Ubuntu 32-bit/64-bit"}
    versions["1.8.1"] = {
        "mac": "Mac OSX", "windows": "Windows Server 64-bit/32-bit", "centos": "Centos 32-bit/64-bit",
        "ubuntu": "Ubuntu 32-bit/64-bit"}
    c = Context({"versions": versions})
    return HttpResponse(t.render(c))


def details(request):
    logger = logging.getLogger('dashboard')
    artifacts = list()
    version = request.GET.get('version')
    license = request.GET.get('license') or 'community'
    os = request.GET.get('os')
    #read all builds from couchbase server
    couchbase = CbClient("localhost", 8091, "Administrator", "password")
    logger.error("connected to couchbase")
    allbuilds = couchbase.query(bucket='default', ddoc='builds', view='metadata', limit=20000)
    #logger.error(allbuilds["rows"])
    #populate builds
    #  emit(doc.name, [doc.name,doc.url,doc.fullversion,doc.arch,doc.version]);
    for item in allbuilds["rows"]:
        value = item["value"]
        if value["fullversion"].find("toy") >= 0:
            continue
        value['buildnumber'] = value["fullversion"][value["fullversion"].find("-")+1:value["fullversion"].rfind("-")]
        license_match = value["name"].find(license) > 0
        logger.error("license_match %s for %s" % (license_match, value["name"]))
        arch_display_name = ''
        if value["arch"] == "x86_64":
            arch_display_name = "64-bit"
        else:
	        arch_display_name = "32-bit"
        if version == value["version"] and os == value["os"] and license_match is True:
            artifact_item = {"name": value["name"],"url": value["url"], 
                             "fullversion": value["fullversion"],"arch": arch_display_name, 
                             "buildnumber": int(value['buildnumber']),"os": value["os"]}
            #get the manifest if it exists ?
            artifact_item["manifest"] = manifest_for_build(value["fullversion"]) or "not fond"
            artifacts.append(artifact_item)

    couchbase.close()
    os_display_name = ''
    if os == 'rpm':
        os_display_name = 'Centos'
    elif os == 'deb':
        os_display_name = 'Ubuntu'
    elif os == 'windows':
        os_display_name = 'Windows'
    title = "%s builds ( 32-bit and 64-bit) %s edition" % (os_display_name, license)
    artifacts = DataHelper.multikeysort(artifacts, ['buildnumber'])
    return render_to_response('../templates/dashboard/details.html',
            {'title': title, 'data': artifacts})


def _download(url):
    logger = logging.getLogger('dashboard')
    logger.error("downloading %s" % (url))
    try:
        import urllib

        file = urllib.urlopen(url)
        content = file.read()
        file.close()
        if content.find("404 Not Found") == -1:
            return content
        else:
            return ""
    except:
        return ""


def _to_json(manifest, fullversion):
    from xml.dom.minidom import parseString

    dom = parseString(manifest)
    projects = dom.getElementsByTagName("project")
    projects_commits = []
    for project in projects:
        commit = {"fullversion": fullversion}
        for (name, value) in project.attributes.items():
            if name == "name":
                commit["name"] = value
            if name == "revision":
                commit["revision"] = value
        projects_commits.append(commit)
    return projects_commits


def _get_commits_description(commits_dict):
    commits_descriptions = []
    for a_commit in commits_dict:
        try:
            a_description = {"name": a_commit["name"], "commit": a_commit["revision"]}
            repo = Repo("/space/repo/couchbase-2.0/%s" % (a_commit["name"]))
            commit = repo.commit(a_commit["revision"])
            a_description["message"] = commit.message
            a_description["author"] = commit.author
            commits_descriptions.append(a_description)
        except:
            pass
    return commits_descriptions

def populate_commits(request):
    """
        for each commit create an entry in couchbase
    """
    logger = logging.getLogger('dashboard')
    project = request.GET.get('project')
    refs = request.GET.get('refs')
    couchbase = CouchbaseClient("http://localhost:8091/pools/default", "default", "")    
    refs = request.GET.get('refs')
    gp = GitPopulate("/space/repo/couchbase-2.0/", project, refs)
    commits = gp.fetch_commits()
    for commit in commits["tree"]:
        key = "%s-%s" % (commit["project"], commit["revision"])
        value = json.dumps(commit).encode('ascii', 'ignore')
        key = key.encode('ascii', 'ignore')
        couchbase.set(key, 0, 0, value)
    key = '%s' % (project)
    couchbase.set(key.encode('ascii', 'ignore'), 0, 0, 
                  json.dumps(commits).encode('ascii', 'ignore'))
    couchbase.done()
    return render_to_response('../templates/dashboard/empty.html')



def populate_all_manifests(request):
    logger = logging.getLogger('dashboard')
    couchbase = CouchbaseClient("http://localhost:8091/pools/default", "default", "")
    cbclient= CbClient("localhost", 8091, "Administrator", "password")
    qr = cbclient.query(bucket='default', ddoc='builds', view='manifests', limit=20000)
    for item in qr["rows"]:
        doc = item["value"]
        if doc["name"].find("-manifest.xml") == -1:
            #        if doc["name"].find("-manifest.xml") == -1 and 'commits' not in doc:
            manifest_commits = ManifestPopulate(doc, doc["url"]).json()
            doc['commits'] = manifest_commits
            couchbase.set(doc['name'].encode('ascii','ignore'), 0, 0,
                          json.dumps(doc).encode('ascii','ignore'))
            logger.info("retreived git commits for %s" % (doc['name']))
    return render_to_response('../templates/dashboard/empty.html')
    
# how to 

def gitx(request):
    '''
        get all commits for this project
        for top 20 , do view call to find out the builds
    '''
    logger = logging.getLogger('dashboard')
    project = request.GET.get('project')
    limit = request.GET.get('limit')
    couchbase = CouchbaseClient("http://localhost:8091/pools/default", "default", "")
    cbclient= CbClient("localhost", 8091, "Administrator", "password")
    a,b,value = couchbase.get(project.encode('ascii','ignore'))
    commits = json.loads(value)["tree"]
    counter = 0
    data = list()
    for commit in commits:
        commit["builds"]=[]
        counter = counter + 1
        filter_value = "\"%s-%s\"" % (project, commit["revision"])
        params={"startkey":filter_value,"endkey":filter_value}
        qr = cbclient.query(bucket='default', ddoc='builds', view='commits', limit=100,params=params)
        for item in qr["rows"]:
            logger.error(commit["builds"])
            fullversion = item["value"][1].encode('ascii','ignore')
            if fullversion not in commit["builds"]:
                commit["builds"].append(fullversion)
        data.append(commit)
        end_index = commit["message"].find("\n") or len(commit["message"] - 1)
        commit["message"] = commit["message"][0:end_index]
        if counter == limit:
            break

    return render_to_response('../templates/dashboard/commits.html',
                          {'title': 'commits', 'data': data})
            
    
    
#    6dab6744c77a1f044017e0b79573185264f7bb09
#    couchbase.done()
#    cbclient.close()


def manifest_for_build(buildnumber):
    logger = logging.getLogger('manifest_for_build')
    couchbase = CbClient("localhost", 8091, "Administrator", "password")
    manifests = manifests = couchbase.query(bucket='default', ddoc='builds', view='manifests', limit=20000,
        params={"startkey": "\"" + buildnumber + "\""})
    result = []
    for item in manifests["rows"]:
        result.append(item["value"])
    return result


def manifest(request):
    logger = logging.getLogger('dashboard')
    package_type = request.GET.get('package_type')
    fullversion = request.GET.get('fullversion')
    couchbase = CbClient("localhost", 8091, "Administrator", "password")
    manifests = couchbase.query(bucket='default', ddoc='builds', view='manifests', limit=20000,
        params={"startkey":"\"1.8.1-901-rel\""})

    descriptions = {}
    for item in manifests["rows"]:
        logger.error(package_type)
        value = item["value"]
        logger.error(value)
        if value["name"].find(package_type) >= 0:
            url = value["url"]
            logger.error("downloading manifest from url %s" % (url))
            content = _download(url)
            logger.error(content)
            to_json = _to_json(content, fullversion)
            logger.error(to_json)
            descriptions = _get_commits_description(to_json)
            logger.error(descriptions)
            id = value["name"]
            value
            break
            #convert to json
            #for each project get the git description
            #jsonbuild
    # update database....
    return render_to_response('templates/dashboard/manifest.html',
            {'title': 'manifests', 'data': descriptions})

    #for each key value get the message and description and then print this out in a
    #for where we have a table column 1 is project , 2 is commit id and then thrird column has
    # the description

