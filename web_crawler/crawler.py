import os
import re
import time
from mongodb import RedHatKBStateDB 
from login import RedHatLogin
import config
from threading import Thread

begin = 1030845
end = 1030846
work_size = (end - begin) / config.THREAD_NUM
 
class RedHatCrawler():

    def __init__(self ):
        self.rh_kb_state_db = RedHatKBStateDB()   
        self.working_thread = []

    def download_files(self, low, high):
        for i in range(low, high):
            url = "https://access.redhat.com/solutions/%d" %(i) 
            if self.rh_kb_state_db.is_url_downloaded(url):
                continue
            cmd = "wget --force-directories -c --load-cookies " + config.COOKIES_FILENAME + " " + url
            ret_code = os.system(cmd)
            if ret_code == 2048:
                continue
            # TODO: add login state restart 
            self.rh_kb_state_db.update(url, ret_code == 0)
#        thread.exit_thread()
    
    def start(self):
        login = RedHatLogin()
        if login.login() == False:
            print "Can not login RedHat"
            return
        login.dump_cookies()
        low = begin
        high = min(low + work_size, end)
        while low < high:
            t = Thread(target = self.download_files, args = (low, high))
            t.start()
            low = high
            high = min(low + work_size, end)
            self.working_thread.append(t)
        for t in self.working_thread:
            t.join() 

class IKBCrawler():

    def __init__(self ):
        self.working_thread = []

    def download_files(self, low, high):
        for i in range(low, high):
            url = "\"https://ikb.vmware.com/contactcenter/php/search.do?cmd=displayKC&docType=kc&externalId=%d&sliceId=1&docTypeID=DT_KB_1_1&dialogID=654982245\"" %(i)
            cmd = "wget -c --load-cookies " + config.IKB_COOKIES_FILENAME + " " + url
            cmd += " -O ikb/%d" %(i)
            print cmd
            ret_code = os.system(cmd)
            if ret_code == 2048:
                continue
            # TODO: add login state restart 
#        thread.exit_thread()
    
    def start(self):
        low = begin
        high = min(low + work_size, end)
        while low < high:
            t = Thread(target = self.download_files, args = (low, high))
            t.start()
            low = high
            high = min(low + work_size, end)
            self.working_thread.append(t)
        for t in self.working_thread:
            t.join() 

if __name__ == "__main__":
    mycrawler = IKBCrawler()
    mycrawler.start()
