from datetime import datetime
from elasticsearch import Elasticsearch
from webpage import RedHatKBPage
from os import listdir
from os.path import isfile, join

class RHKB_to_ES_Loader:

###############################################
# RedHat Database structure:
#    KBid, URL, Issue, Environment, Resolution 
###############################################

    def __init__(self, dir):
        self.es = Elasticsearch()
        self.index = 'redhat_kb'
        self.doc_type = 'kb'
        self.kb_dir = dir 

    def index_item(self, page):
        if page.is_en_page() == False:
            print "INFO: It is not an en page"
            return False
        doc = {
            'url': page.get_url(),
            'issue': page.get_issue(),
            'env': page.get_env(),
            'resolution': page.get_resolution()
        }
        res = self.es.index(index = self.index, doc_type = self.doc_type, id = page.get_id(), body = doc)
        return res['created']

    def index_all(self):
        # iter all kbs
        for f in listdir(self.kb_dir):
            print "DEBUG: %s" %(f)
            file = join(self.kb_dir, f)
            if isfile(file):
                self.index_item(RedHatKBPage(file))

if __name__ == "__main__":
    import sys
    print len(sys.argv)
    if len(sys.argv) < 2:
        print "Please provide KB dirname"
        exit(0)
    
    loader = RHKB_to_ES_Loader(sys.argv[1])
 
    print loader.index_all()
