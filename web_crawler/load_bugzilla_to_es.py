from datetime import datetime
from elasticsearch import Elasticsearch
from webpage import RedHatKBPage
from os import listdir
from os.path import isfile, join
from db_con import get_bz_con

class VMBugzilla_to_ES_Loader:

##############################################################################
# VMBugzilla Database structure: 
#    bugid(0), title(9), text(11) (essential part for full text search)
#       opened(1), severity(2), priority(3), status(4), assignee(5), reporter(6),
#       category(7), component(8), fixby(10)(for result display)
##############################################################################

    def __init__(self):
        self.es = Elasticsearch()
        self.index = 'bugzilla'
        self.doc_type = 'text'
        self.bz_con, self.bz_cur = get_bz_con()

    def create_item(self, bugid):
        sql='select bug_id, creation_ts, bug_severity, priority, bug_status, assigned_to, reporter, category_id, component_id, short_desc from bugs where bug_id = %d' %(bugid)
        self.bz_cur.execute(sql)
        item = self.bz_cur.fetchall()
    
        assert(len(item) == 1)
        ans = list(item[0])
        
        # handle time
        ans[1] = str(ans[1]).split()[0]

        # replace userid by login_name  
        sql='select login_name from profiles where userid = %s' %(ans[5])
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        ans[5] = name[0][0]
   
        sql='select login_name from profiles where userid = %s' %(ans[6])
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        ans[6] = name[0][0] 
   
        # replace category_id by category name
        sql= 'select name from categories where id=%s' %(ans[7]) 
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        ans[7] = name[0][0] 
    
        # replace component_id by component name
        sql= 'select name from components where id=%s' %(ans[8]) 
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        ans[8] = name[0][0]

        # generate fixby
        fixby = ""
        sql = 'select product_id, version_id, phase_id from bug_fix_by_map where bug_id=%d' %(bugid)
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        product_id = name[0][0]
        version_id = name[0][1]
        phase_id = name[0][2]
        sql = 'select name from products where id=%d' %(product_id)
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        if (len(name) > 0):
            fixby += name[0][0]
        sql = 'select name from versions where id=%d' %(version_id)
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        if (len(name) > 0):
            fixby += " "
            fixby += name[0][0]
        sql = 'select name from phases where id=%d' %(phase_id)
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        if (len(name) > 0):
            fixby += " "
            fixby += name[0][0]
        ans.append(fixby)
        
        # generate thetext
        #    SQL: select group_concat(thetext) from longdescs group by bug_id limit %d,1' %(bugid)
        #       is too slow
        sql = 'set group_concat_max_len = 10240000'
        self.bz_cur.execute(sql)
        sql = 'select group_concat(thetext) from \
            (select thetext from longdescs where bug_id = %d) as myalias' %(bugid)
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        # add unicode to avoid json dumps error
        text = unicode(name[0][0], errors='replace')
        ans.append(text)          
        
        return ans

    def index_item(self, item):
        doc = {
            # title seems to be a reversed filed, change to summary
            'summary': item[9],
            'opened': item[1],
            'severity': item[2],
            'priority': item[3],
            'status': item[4],
            'assignee': item[5],
            'reporter': item[6],
            'category': item[7],
            'component': item[8],
            'fixby': item[10],
            'text': item[11]
        }
        #print doc
        res = self.es.index(index = self.index, doc_type = self.doc_type, id = item[0], body = doc)
        return res['created']

    def index_all(self):
        # iter all
        sql = 'select max(bug_id) from bugs'
        self.bz_cur.execute(sql)
        name = self.bz_cur.fetchall()
        max_bugid = int(name[0][0])
        print "max:" + str(max_bugid)
        for i in range(1, max_bugid + 1):
            tmp = self.create_item(i)
        #    print tmp
            self.index_item(tmp)

if __name__ == "__main__":
    import sys
    
    loader = VMBugzilla_to_ES_Loader()

    #print loader.create_item(1291688)
    #print loader.create_item(1335744)
    #print loader.create_item(1339158)
    loader.index_all()
