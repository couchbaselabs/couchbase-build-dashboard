class Build(object):

#version , build #  , link , manifest
    def __init__(self, info):
        self.version = info["version"]
        self.product = info["product"]
        self.link = info["link"]
        self.manifest = info["manifest"]
        self.os = info["os"]
        self.arch = info["arch"]
        self.type = info["type"]


    def json(self):
        return {"version": self.version,
                "product": self.product,
                "link": self.link,
                "manifest": self.manifest,
                "os": self.os,
                "arch": self.arch,
                "type": self.type}


class Manifest(object):
    def __init__(self, info):
        self.build_id = info["build_id"]
        self.link = info["link"]
        #descriptions = {"couchdb":[{"git_commit":"description"},{"git_commit_2":"description2"}],"ep-engine":[]}
        self.descriptions = {}

    def json(self):
        return {"build": self.build_id,
                "link": self.link}
