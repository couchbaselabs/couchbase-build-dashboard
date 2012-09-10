import json

from django.conf import settings

from rest_client import RestConnection
import memcache

class CbClient:
    """Abstract couchbase client"""

    def __init__(self, host=None, port=None, username=None, password=None):
        """Initialize memcache and couchbase clients"""

        server = {'ip': host or settings.COUCHBASE['HOST'],
                  'port': port or settings.COUCHBASE['PORT'],
                  'username': username or settings.COUCHBASE['USER'],
                  'password': password or settings.COUCHBASE['PASSWORD']}

        self.rest_client = RestConnection(server)

        self.mc_client = memcache.Client([server['ip'] + ':11211'], debug=0)

    def insert(self, test_id, doc={}):
        doc = json.dumps(doc)
        return self.mc_client.set(str(test_id), doc)

    def find(self, test_id):
        try:
            doc = self.mc_client.get(str(test_id))
            return json.loads(doc)
        except (TypeError, ValueError) as error:
            print error
            return {}

    def update(self, test_id, doc={}):
        current = self.find(test_id)
        current.update(doc)
        return self.insert(test_id, current)

    def query(self, bucket='default', ddoc='', view='', params=[], limit=5000):
        return self.rest_client.view_results(bucket, ddoc, view, params, limit)

    def close(self):
        try:
            self.mc_client.close()
        except:
            pass
