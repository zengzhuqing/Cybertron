from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import os
import config

class RedHatLogin():
    
    def __init__(self):
        self.login_url = 'https://idp.redhat.com/idp'
        self.username = config.USERNAME 
        self.password = config.PASSWORD
        self.cookies_filename = config.COOKIES_FILENAME
        self.browser = webdriver.Firefox()
        self.all_cookies = []
        self.login_state = False   
 
    # Translate cookies item to cookies.txt format
    # reference to http://superuser.com/questions/666167/how-do-i-use-firefox-cookies-with-wget
    def translate_cookies_item(self, item):
        domain = item[u'domain']
        flag = 'TRUE'
        path = item[u'path']
        secure = str(item[u'secure']).upper()
        expiration = '0' if item[u'expiry'] == None else str(item[u'expiry'])
        name = item[u'name']
        value = item[u'value'] 
        return domain + '\t' + flag + '\t' + path + '\t' + secure + '\t' + expiration + '\t' + name + '\t' + value 

    def login(self):
        self.browser.get('https://idp.redhat.com/idp')
        element_username = self.browser.find_element_by_name('j_username')
        element_username.send_keys(self.username)
        element_password = self.browser.find_element_by_name('j_password')
        element_password.send_keys(self.password + Keys.RETURN)
        # wait for login ready  
        sleep(5)
        # Get cookies
        self.all_cookies = self.browser.get_cookies()
        return self.check_login_state()    
 
    def check_login_state(self):
        for item in self.all_cookies:
            if 'rh_sso' == item[u'name']:
                self.login_state = True
                break
        return self.login_state           

    def dump_cookies(self):
        with open(self.cookies_filename, 'w') as cookies_file:
            for item in self.all_cookies:
                cookies_file.write(self.translate_cookies_item(item) + '\n')
        self.browser.quit()

class iKBLogin():
    
    def __init__(self):
        self.login_url = 'https://hrzn-prod-ec-2.vmware.com/login/'
        self.username = config.VM_ID
        self.password = config.VM_PASSWD
        self.cookies_filename = config.IKB_COOKIES_FILENAME
        self.browser = webdriver.Firefox()
        self.all_cookies = []
        self.login_state = False   
 
    # Translate cookies item to cookies.txt format
    # reference to http://superuser.com/questions/666167/how-do-i-use-firefox-cookies-with-wget
    def translate_cookies_item(self, item):
        domain = item[u'domain']
        flag = 'TRUE'
        path = item[u'path']
        secure = str(item[u'secure']).upper()
        expiration = '0' if item[u'expiry'] == None else str(item[u'expiry'])
        name = item[u'name']
        value = item[u'value'] 
        return domain + '\t' + flag + '\t' + path + '\t' + secure + '\t' + expiration + '\t' + name + '\t' + value 

    def login(self):
        self.browser.get(self.login_url)
        element_username = self.browser.find_element_by_name('username')
        element_username.send_keys(self.username)
        element_password = self.browser.find_element_by_name('password')
        element_password.send_keys(self.password + Keys.RETURN)
        # wait for login ready  
        sleep(5)
        
        body = self.browser.find_element_by_tag_name("body")
        body.send_keys(Keys.CONTROL + 't')
        self.browser.get("https://ikb.vmware.com/contactcenter/php/search.do?cmd=displayKC&docType=kc&externalId=1030845&sliceId=1&docTypeID=DT_KB_1_1&dialogID=654982245&stateId=1%200%20654984785")
        sleep(25)
        # Get cookies
        self.all_cookies = self.browser.get_cookies()
        print self.all_cookies
        return self.check_login_state()    
 
    def check_login_state(self):
        for item in self.all_cookies:
            if 'rh_sso' == item[u'name']:
                self.login_state = True
                break
        return self.login_state           

    def dump_cookies(self):
        with open(self.cookies_filename, 'w') as cookies_file:
            for item in self.all_cookies:
                cookies_file.write(self.translate_cookies_item(item) + '\n')
        self.browser.quit()

if __name__ == "__main__":
    login = iKBLogin()
    print login.login()
    login.dump_cookies()
