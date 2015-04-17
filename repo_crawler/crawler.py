import os
import sys
import re
import time
from database import QueueDB, WebpageDB, DuplCheckDB
from mongodb import RepoStateDB 
from downloader import DownloadManager
from webpage import WebPage
import config

class Crawler():

    def __init__(self ):
        self.downloader = DownloadManager()
        self.webpage = None
        self.init_database()
        self.rules = {}
        self.files = []
        self.file_rule = ".+"

    def init_database(self):
        self.queue = QueueDB('queue.db')
        self.webpagedb = WebpageDB('webpage.db')
        self.duplcheck = DuplCheckDB('duplcheck.db')
        self.repodb = RepoStateDB()   
 
    def add_seeds(self, links):
        new_links = self.duplcheck.filter_dupl_urls(links)
        self.duplcheck.add_urls(new_links)
        self.queue.push_urls(new_links)
    
    def add_rules(self, rules):
        self.rules = {}
        for url, inurls in rules.items():
            reurl = re.compile(url)
            repatn = []
            for u in inurls:
                repatn.append(re.compile(u))
            self.rules[reurl] = repatn

    def set_file_rule(self, rule):
        self.file_rule = rule

    def get_patterns_from_rules(self,url):
        patns = []
        for purl,ru in self.rules.items():
            if purl.match(url)!= None:
                patns.extend(ru)
        return list(set(patns))
    
    def download_files(self, files):
        for f in files:
            #cmd = "wget --force-directories -c " + f + " -P " + config.repos_dir
            cmd = "wget -c " + f + " -P " + config.repos_dir
            ret_code = os.system(cmd)
            self.repodb.update(f, ret_code == 0)

    def start(self):
        while 1:
            url = self.queue.pop_url()
            print url
            if url == None:
                print "crawling task is done."
                break
            error_msg, url, redirected_url, html = self.downloader.download(url)
    #        print error_msg, url, redirected_url, html
            if html !=None:
                self.webpagedb.html2db(url,html)
 
                self.webpage = WebPage(url,html)
                self.webpage.parse_links()
                ruptn = self.get_patterns_from_rules(url)
                #print ruptn
                links = self.webpage.filter_links(tags = ['a'], patterns= ruptn)
                print links
                self.add_seeds(links)
                file_pattern = []
                file_pattern.append(re.compile(self.file_rule))
                files = self.webpage.filter_links(tags = ['a'], patterns = file_pattern)
                self.files.append(files)
                #TODO:
                self.download_files(files)
                print files

    def mysleep(self, n):
        for i in range(n):
            time.sleep(1)
            print "sleep",i,"of",n

if __name__ == "__main__":
    # Centos repo crawler
    centos_crawler = Crawler()
    # Be careful: if seed is a dir, make sure you add / in the end
    centos_crawler.add_seeds(['http://debuginfo.centos.org'])
    rules = {'^http://debuginfo\.centos\.org(.*)$':['^http://debuginfo\.centos\.org/(.+)/$']}
    #rules = {'^http://debuginfo\.centos\.org/6(.*)$':['^(.+)/$']}
    
    # To-test, suse and ubuntu debuginfo package crawler
    
    centos_crawler.add_rules(rules)
    centos_crawler.set_file_rule("^.+kernel-debuginfo-.+\.rpm$")
    centos_crawler.start()
    
    # OpenSuse repo crawler
    opensuse_crawler = Crawler()
    opensuse_crawler.add_seeds(['http://ftp5.gwdg.de/pub/opensuse/discontinued/debug/'])
    rules = {'^http://ftp5\.gwdg\.de/pub/opensuse/discontinued/debug/(.*)$':['^http://ftp5\.gwdg\.de/pub/opensuse/discontinued/debug/(.+)/$']}
    
    opensuse_crawler.add_rules(rules)
    opensuse_crawler.set_file_rule("^(.+)kernel-default-debuginfo-(.+)\.rpm$")
    opensuse_crawler.start()
    
    # Ubuntu repo crawler
    ubuntu_crawler = Crawler()
    ubuntu_crawler.add_seeds(['http://ddebs.ubuntu.com/pool/main/l/linux/'])
    rules = {'^http://ddebs\.ubuntu\.com/pool/main/l/linux/(.*)$':['^http://ddebs\.ubuntu\.com/pool/main/l/linux/(.+)/$']}
    
    ubuntu_crawler.add_rules(rules)
    ubuntu_crawler.set_file_rule("^linux-image-(.+)\.ddeb$")
    ubuntu_crawler.start()
