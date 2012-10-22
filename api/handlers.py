from viewcouchbase.client import CbClient
from piston.handler import BaseHandler
from piston.utils import rc
from django import forms
from couchbase.couchbaseclient import CouchbaseClient
import logging
import re
import json

class RawBuildNameDecodedHelper(object):
    @staticmethod
    def is_substring(list, item):
        if item:
            for l in list:
                if item.find(l) >= 0:
                    return True
        return False


    @staticmethod
    def populate_build_meta(name):
        data = {}
        if name.find("couchbase-server") >= 0:
            data["product"] = "couchbase-server"
        if name.find("moxi-server") >= 0:
            data["product"] = "moxi-server"
        if name.find("community") >= 0:
            data["license"] = "community"
        if name.find("enterprise") >= 0:
            data["license"] = "enterprise"
        if "product" in data and data["product"] == "couchbase-server":
            if name.find("x86_64") >= 0:
                data["arch"] = "x86_64"
            elif name.find("x86") >= 0:
                data["arch"] = "x86"
            if name.find(".zip") >= 0:
                data["os"] = "mac"
                data["package"] = "zip"
            if name.find(".dmg") >= 0:
                data["os"] = "mac"
                data["package"] = "dmg"
            if name.find(".deb") >= 0:
                data["os"] = "deb"
                data["package"] = "deb"
            if name.find(".rpm") >= 0:
                data["os"] = "rpm"
                data["package"] = "rpm"
            if name.find(".rpm") >= 0:
                data["os"] = "rpm"
                data["package"] = "rpm"
            if name.find("setup.exe") >= 0:
                data["os"] = "windows"
                data["package"] = "exe"
            if name.find(".manifest.xml") >= 0:
                data["os"] = ""
                data["package"] = "manifest"
            if name.find(".md5") >= 0:
                data["package"] = "md5"
            if "package" in data:
                if name.find("1.8.1-") >= 0:
                    data["version"] = "1.8.1"
            if re.search(r'\d\.\d\.\d-\d*-\w\w\w', name):
                data["fullversion"] = re.search(r'\d\.\d\.\d-\d*-\w\w\w', name).group()
            if name.find("2.0.0-") >= 0:
                data["version"] = "2.0.0"
            if re.search(r'\d\.\d\.\d-\d*-\w\w\w', name):
                data["fullversion"] = re.search(r'\d\.\d\.\d-\d*-\w\w\w', name).group()
            data["url"] = "http://builds.hq.northscale.net/latestbuilds/%s" % (name)
            if "arch" not in data:
                data["arch"] = "unknown"
        return data


class BuildDatabasePopulateRestHandler(BaseHandler):
    allowed_methods = ('POST')

    def create(self, request):
        logger = logging.getLogger('dashboard')
        couchbase = CouchbaseClient("http://localhost:8091/pools/default", "default", "")
        kv_data = {}
        json_data = json.loads(request.raw_post_data)
        for object in json_data:
            name = json_data[object]
            skip_tokens = ["CHANGES", "1.7", "1.8.1r", "preview-", "-manifest"]
            if not RawBuildNameDecodedHelper.is_substring(skip_tokens, name):
                data = RawBuildNameDecodedHelper.populate_build_meta(name)
                kv_data[name] = data

        result = {}
        num_updated_rows = 0
        for key in kv_data:
            item = kv_data[key]
            if "package" not in item or "fullversion" not in item:
                continue
            item = kv_data[key]
            _id = "%s-%s-%s-%s" % (item["package"], item["arch"],
                                   item["os"], item["fullversion"])
            if item["package"] == "manifest":
                content = self._download(item["url"])
                to_json = self._to_json(content, item["fullversion"])
                item["commits"] = to_json
            couchbase.set(_id.encode("ascii", "ignore"), 0, 0, json.dumps(item).encode("ascii", "ignore"))
            num_updated_rows += 1

        logger.info('updated %d rows in the database' % (num_updated_rows))
        return {"status": "ok"}

    def _download(self, url):
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

class BuildRestHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self, request, build_id):
        couchbase = CbClient("localhost", 8091, "Administrator", "password")
        response = []
        allbuilds = couchbase.query(bucket='default', ddoc='builds',
            view='metadata', limit=200, params={"startkey": "\"%s\"" % (build_id)})
        for item in allbuilds["rows"]:
            row = item["value"]
            response.append(row)
        couchbase.close()
        return response


    def create(self, request, *args, **kwargs):
        couchbase = CouchbaseClient("http://localhost:8091/pools/default", "default", "")
        if request.content_type:
            data = request.data
            _id = "%s-%s-%s-%s" % (data["package"], data["arch"], data["os"], data["fullversion"])
            _id = _id.encode("ascii", "ignore")
            couchbase.set(_id, 0, 0, json.dumps(data).encode("ascii", "ignore"))
            couchbase.done()
            return {"status": "ok"}
        else:
            return {"status": "failed", "data": request.data["os"]}

    def update(self, request, build_id):
        return {"status": "ok"}

    def delete(self, request, build_id):
        return {"status": "ok"}
