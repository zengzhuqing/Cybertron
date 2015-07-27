from datetime import datetime
from elasticsearch import Elasticsearch
from webpage import IKBPage
from os import listdir
from os.path import isfile, join

class IKB_to_ES_Loader:

##############################################################################
# RedHat Database structure:
#    KBid, URL, Symptoms, Resolution, Solution, Details, Purpose, Cause, Title
#    search fields name in es: 
#       merge fields "symptoms, resolution, solution, details, purpose, cause" into text
##############################################################################

    def __init__(self, dir):
        self.es = Elasticsearch()
        self.index = 'ikb'
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
        text = ""
        if page.get_symptoms() != None:
            text += page.get_symptoms()
        if page.get_resolution() != None:
            text += page.get_resolution()
        if page.get_solution() != None:
            text += page.get_solution()
        if page.get_cause() != None:
            text += page.get_cause()
        if page.get_purpose() != None:
            text += page.get_purpose()
        if page.get_details() != None:
            text += page.get_details()
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
                self.index_item(IKBPage(file))

if __name__ == "__main__":
    import sys
    print len(sys.argv)
    if len(sys.argv) < 2:
        print "Please provide KB dirname"
        exit(0)
    
    loader = IKB_to_ES_Loader(sys.argv[1])
 
    print loader.index_all()
