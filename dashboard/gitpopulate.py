import json
from git import *
import logging

class GitPopulate(object):

    def __init__(self, path, project, refs):
        self.path = path
        self.project = project
        self.refs = refs

    def fetch_commits(self):
        logger = logging.getLogger('dashboard')
        commits = {"name":self.project,"refs":self.refs,"tree":[]}
        a_commit = {"project":self.project}
        repo = Repo("%s/%s" % (self.path, self.project))
        git_commits = repo.iter_commits(self.refs, max_count=2000)
        logger.error(self.path)
        logger.error(self.project)
        logger.error(self.refs)
        for c in git_commits:
            logger.error(c.message)
            commits["tree"].append({"project":self.project,
                        "message":c.message,
                        "author":str(c.author),
                        "revision":c.hexsha})
        return commits



