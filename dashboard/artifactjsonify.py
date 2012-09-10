import json
from couchbase.couchbaseclient import CouchbaseClient
import re

json_data = json.loads(open("/tmp/data.json").read())
kv_data = {}
for object in json_data:
    data = {}
    #data = json_data[object]
    data["name"] = json_data[object]
    name = data["name"]
#    print name
    if name.find("CHANGES") >= 0 or name.find("1.7") >= 0 or name.find("preview-") >= 0 or name.find("-manifest.xml") >= 0:
        continue
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
        data["url"] = "http://builds.hq.northscale.net/latestbuilds/%s" % (data["name"])
        if "arch" not in data:
            data["arch"] = "unknown"
        kv_data[data["name"]] = data

result = {}
for item in kv_data:
    if "package" not in kv_data[item] or "fullversion" not in kv_data[item]:
        continue
    result[item] = kv_data[item]

with open('/tmp/jsonified.json', 'wb') as fp:
    json.dump(result, fp)

c = CouchbaseClient("http://localhost:8091/pools/default", "default", "")
#id will be product-architechture-package-fullversion
print len(result)
for item in result:
    _id = "%s-%s-%s-%s" % (result[item]["package"], result[item]["arch"],
                           result[item]["os"], result[item]["fullversion"])
    c.set(_id.encode("ascii", "ignore"), 0, 0, json.dumps(result[item]).encode("ascii", "ignore"))
all_names = {"list":[]}
for item in result:
    all_names["list"].append(item.encode("ascii", "ignore"))
c.set("all-builds", 0, 0, json.dumps(all_names).encode("ascii", "ignore"))


