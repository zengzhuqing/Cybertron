import pymongo

class CrawlerMongoDB:
    def __init__(self):
        self.con = pymongo.Connection('localhost', 27017)
        self.database = self.con.crawler

class RepoStateDB( CrawlerMongoDB ):
    
    def __init__(self):
        CrawlerMongoDB.__init__(self)
        self.table = self.database.state
   
    def remove(self, url):
        self.table.remove({'url':url})
 
    def update(self, url, state):
        self.table.update({'url':url}, {'url':url, 'state':state}, True)

if __name__ == "__main__":
    test = RepoStateDB()
    test.update("www.aaa", True) 
    test.update("www.bbb", False) 
