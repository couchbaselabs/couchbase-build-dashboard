import os
import json

files = os.listdir("/home/buildbot/latestbuilds")
post_data = {}
for f in files:
    post_data[f] = f

file = open("/tmp/a.json","w+")
file.write(json.dumps(post_data))
file.close()

print post_data



import httplib

conn = httplib.HTTPConnection('localhost', 8080)
conn.connect()
request = conn.putrequest('POST', 'api/populate')
headers = {}
headers['Content-Type'] = 'application/json'
headers['User-Agent'] = 'Envjs/1.618 (SpyderMonkey; U; Linux x86_64 2.6.38-10-generic;  pl_PL.utf8; rv:2.7.1) Resig/20070309 PilotFish/1.3.pre03'
headers['Accept'] = '*/*'
for k in headers:
    conn.putheader(k, headers[k])
conn.endheaders()

conn.send(post_data)

resp = conn.getresponse()
print resp.status
print resp.reason
print resp.read()

conn.close()