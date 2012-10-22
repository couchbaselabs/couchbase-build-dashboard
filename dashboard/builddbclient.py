import sys
import os
import json
import httplib
import requests
directory = sys.argv[1]
files = os.listdir(directory)

#file = open("/tmp/a.json","w+")
#file.write(json.dumps(post_data))
#file.close()

for f in files:
   post_data = {f:f}
   print "sending : ", post_data
   headers = {'Content-type': 'application/json', 'Accept': '*/*'}
   resp = requests.post("http://localhost:8080/api/populate",
      data=json.dumps(post_data), headers=headers)
   print resp
