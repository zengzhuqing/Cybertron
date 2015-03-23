import pymongo

class CrawlerMongoDB:
    def __init__(self):
        self.con = pymongo.Connection('localhost', 27017)
        self.database = self.con.crawler

class RedHatKBStateDB( CrawlerMongoDB ):
    
    def __init__(self):
        CrawlerMongoDB.__init__(self)
        self.table = self.database.rh_kb_state
   
    def remove(self, url):
        self.table.remove({'url':url})
 
    def update(self, url, state):
        self.table.update({'url':url}, {'url':url, 'state':state}, True)

    def is_url_downloaded(self, url):
        return self.table.find_one({'url':url}, {'state':True}) != None 

if __name__ == "__main__":
    test = RedHatKBStateDB()
   # test.update("www.aaa", True) 
   # test.update("www.bbb", False)
    print test.is_url_downloaded("https://access.redhat.com/solutions/207253") 
