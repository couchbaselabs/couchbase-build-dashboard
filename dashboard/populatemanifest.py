import logging
import json
from xml.dom.minidom import parseString

class ManifestPopulate(object):

    def __init__(self, manifest, url):
        self.manifest = manifest
        self.url = url

    def _download(self, url):
        logger = logging.getLogger('dashboard')
        logger.info("downloading %s" % (url))
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

    def json(self):
        xml = self._download(self.url)
        return self._to_json(xml, self.manifest["fullversion"])
        

    def _to_json(self, xml, fullversion):
        dom = parseString(xml)
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