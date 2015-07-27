import lxml.html    # python-lxml
import urlparse
import re
import os

class WebPage:
    
    ###########################################
    #   WEBPAGE CONSTRUCTOR
    ###########################################
    def __init__(self, url, html):
        self.url = url
        self.html = html
        self.doc = lxml.html.fromstring(self.html)
        self.links = {}

    #######################################
    # parsing links from html page
    #######################################
    def parse_links(self):
        for elem, attr, link, pos in self.doc.iterlinks():
            absolute = urlparse.urljoin(self.url, link.strip())
            #print elem.tag ,attr, absolute, pos
            if elem.tag in self.links:
                self.links[elem.tag].append(absolute)
            else:
                self.links[elem.tag] = [absolute]
        return self.links

    # filter links
    def filter_links(self,tags=[],patterns=[]):
        #CHANGES Apr 17 2011 START
        #patterns = []
        #for p in str_patterns:
        #    patterns.append(re.compile(p))
        #CHANGES Apr 17 2011 E N D
        ##
        filterlinks = []
        if len(tags)>0:
            for tag in tags:
                for link in self.links[tag]:
                    if len(patterns) == 0:
                        pass
                        #filterlinks.append(link)
                    else:
                        for pattern in patterns:
                            if pattern.match(link)!=None:
                                filterlinks.append(link)
                                continue
        else:
            for k,v in self.links.items():
                for link in v:
                    if len(patterns) == 0:
                        pass
                        #filterlinks.append(link)
                    else:
                        for pattern in patterns:
                            if pattern.match(link)!=None:
                                filterlinks.append(link)
                                continue

        return list(set(filterlinks))

        return filterlinks    

class RedHatKBPage( WebPage ):

    def __init__(self, filename):
        self.id = os.path.basename(filename)
        url = "https://access.redhat.com/solutions/%s" %(id) 
        with open(filename, 'r') as f:
            html = f.read()
        WebPage.__init__(self, url, html)
        self.aa = 'aaa'
        self.issue_class_name = "field-name-field-kcs-issue-txt"
        self.env_class_name = "field-name-field-kcs-environment-txt"
        self.resolution_class_name = "field-name-field-kcs-resolution-txt"
        self.rootcause_class_name = "field-name-field-kcs-rootcause-txt"
        self.diagnostic_class_name = "field-name-field-kcs-diagnostic-txt"
        self.body_els = self.doc.findall('./body/')
        if len(self.body_els) > 1:
            print "Warning: more than one body in html"
 
    def get_language(self):
        elements = self.doc.findall('./head/meta')
        for e in elements:
            if e.items()[0][0] == 'name' and e.items()[0][1] == 'language':
                return e.items()[1][1]
        return 'en' 
    
    def get_title(self):
        e = self.doc.findall('./head/title')
        if len(e) > 1:
            print "Warning: more than one title in html"
        if len(e) == 0:
            return None
        else:
            return e[0].text_content()
        
    def is_en_page(self):
        return self.get_language() == 'en'

    def get_url(self):
        return self.url    
    
    def get_id(self):
        return self.id 

    def get_issue(self):
        e = self.body_els[0].find_class(self.issue_class_name)
        if len(e) > 1:
            print "Warning: more than one Issue in html"
        if len(e) == 0:
            return None
        else:
            return e[0].text_content().strip()
 
    def get_env(self):
        e = self.body_els[0].find_class(self.env_class_name)
        if len(e) > 1:
            print "Warning: more than one Env in html"
        if len(e) == 0:
            return None
        else:
            return e[0].text_content().strip()
    
    def get_resolution(self):
        e = self.body_els[0].find_class(self.resolution_class_name)
        if len(e) > 1:
            print "Warning: more than one Resolution in html"
        if len(e) == 0:
            return None
        else:
            return e[0].text_content().strip()
        
    def get_rootcause(self):
        e = self.body_els[0].find_class(self.rootcause_class_name)
        if len(e) > 1:
            print "Warning: more than one Root Cause in html"
        if len(e) == 0:
            return None
        else:
            return e[0].text_content().strip()
    
    def get_diagnostic(self):
        e = self.body_els[0].find_class(self.diagnostic_class_name)
        if len(e) > 1:
            print "Warning: more than one Diagnostic Steps in html"
        if len(e) == 0:
            return None
        else:
            return e[0].text_content().strip()

class IKBPage( WebPage ):

    def __init__(self, filename):
        self.id = os.path.basename(filename)
        url = "\"https://ikb.vmware.com/contactcenter/php/search.do?cmd=displayKC&docType=kc&externalId=%s&sliceId=1&docTypeID=DT_KB_1_1&dialogID=654982245\"" %(self.id)
        with open(filename, 'r') as f:
            html = f.read()
        WebPage.__init__(self, url, html)
        self.resolution_class_name = "cc_Resolution"
        self.solution_class_name = "cc_Solution"
        self.details_class_name = "cc_Details"
        self.purpose_class_name = "cc_Purpose"
        self.cause_class_name = "cc_Cause"
        self.symptoms_class_name = "cc_Symptoms"
        self.body_els = self.doc.findall('./body/')
        if len(self.body_els) > 1:
            print "Warning: more than one body in html"
 
    def get_title(self):
        e = self.doc.findall('./head/title')
        if len(e) > 1:
            print "Warning: more than one title in html"
        if len(e) == 0:
            return None
        else:
            return e[0].text_content()
        
    def get_id(self):
        return self.id 

    def get_ele(self, name):
        for ele in self.body_els:
            e = ele.find_class(name)
            if len(e) > 1:
                print "Warning: more than one %s in html" %(name)
            elif len(e) == 0:
                continue
            else:
                return e[0].text_content().strip()
        return None  

    def get_symptoms(self):
        return self.get_ele(self.symptoms_class_name)
    
    def get_cause(self):
        return self.get_ele(self.cause_class_name)

    def get_purpose(self):
        return self.get_ele(self.purpose_class_name)
    
    def get_details(self):
        return self.get_ele(self.details_class_name)

    def get_solution(self):
        return self.get_ele(self.solution_class_name)

    def get_resolution(self):
        return self.get_ele(self.resolution_class_name)
    
    def get_url(self):
        return self.url    

def test_rh_kb(filename):
    page = RedHatKBPage(filename)
    
    print page.get_language()
    print page.get_url()
    print page.get_issue()
    print page.get_env()
    print page.get_resolution()
    print page.get_rootcause()
    print page.get_diagnostic()
    print page.get_title()

def test_ikb(filename):
    page = IKBPage(filename)
    
    print page.get_id()
    print page.get_resolution()
    print page.get_solution()
    print page.get_details()
    print page.get_purpose()
    print page.get_cause()
    print page.get_symptoms()
    print page.get_title()
 
if __name__ == "__main__":
    import sys
    print len(sys.argv)
    if len(sys.argv) < 2:
        print "Please provide KB filename"
        exit(0)
    test_ikb(sys.argv[1])
