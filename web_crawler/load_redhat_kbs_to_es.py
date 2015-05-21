from datetime import datetime
from elasticsearch import Elasticsearch
from webpage import RedHatKBPage
from os import listdir
from os.path import isfile, join

class RHKB_to_ES_Loader:

##############################################################################
# RedHat Database structure:
#    KBid, URL, Issue, Environment, Resolution, Rootcause, Diagnostic, Title
#    search fields name in es: 
#       merge fields "issue, env, resolution, rootcause, diagnostic" into text
##############################################################################

    def __init__(self, dir):
        self.es = Elasticsearch()
        self.index = 'redhat_kb'
        self.doc_type = 'kb'
        self.kb_dir = dir 
        self.create_index()      
    
    def create_index(self): 
        # Create an index with settings and mapping, a line is a term
        #    1. add a new tokenizer which divide by /n
        #    2. add mappings to doc_type and field
        doc = {
            'settings':{
                'analysis':{
                    'analyzer':{
                        'line_tokenizer':{
                            'type':'pattern',
                            'pattern':'\n'
                        }
                    }
                }
            },
            'mappings':{
                self.doc_type:{
                   'properties':{
                        'text':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        },                                      
                        'title':{
                            'type':'string',
                            'analyzer':'line_tokenizer'
                        }                                       
                    } 
                } 
            }
        }
        res = self.es.indices.create(index = self.index, body = doc)
        return res    

    def index_item(self, page):
        if page.is_en_page() == False:
            print "INFO: It is not an en page"
            return False
        text = ""
        if page.get_issue() != None:
            text += page.get_issue()
        if page.get_env() != None:
            text += page.get_env()
        if page.get_resolution() != None:
            text += page.get_resolution()
        if page.get_rootcause() != None:
            text += page.get_rootcause()
        if page.get_diagnostic() != None:
            text += page.get_diagnostic()
        doc = {
            'url': page.get_url(),
            'text': text, 
            'title': page.get_title()
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
