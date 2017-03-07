#-*-coding:utf-8-*-
import re
import urllib2
import urllib
import cookielib
import os
import sys
import time
import json
import StringIO
import gzip 
from bs4 import BeautifulSoup

class Peon:
    def __init__(self):
        self.siteURL = "http://bbs.sgamer.com/forum-44-1.html"
        self.mode = "test"
        self.urlopenTimeOut = 5

    def getUrlContents(self,url):
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request,timeout = self.urlopenTimeOut)
            contents = response.read().decode('utf-8')
        except Exception,e:
            if hasattr(e,"code"):
                print e.code
            if hasattr(e,"reason"):
                print e.reason
            contents = ''   
        return contents

    def getPageContents(self,pageIndex):
        url = self.siteURL
        url = url[:-6]+pageIndex+url[-5:]
        return self.getUrlContents(url)

    def getThreads(self,contents):
        threadsList=list()
        soup = BeautifulSoup(contents, "html.parser")
        #reps = soup.find_all("div")
        #reps = soup.select('tbody[id="normalthread_*"]')
        reps = soup.findAll(name='tbody',attrs={"id":re.compile(r'^normalthread_\d*')})
        #print 'reps = ',reps


        for rep in reps:
            #print rep
            rep_soup = BeautifulSoup(bytes(rep), "html.parser")
            rep_thread = rep_soup.select('th[class="common"]')
            #print rep_thread[0].string[3:],'=',rep_text[0].string

            print rep_soup
            print '***********************************************************************'
            
            threadsList.append(rep_thread)
        return threadsList






peon = Peon()
contents = peon.getPageContents('2')
peon.getThreads(contents)

                              


        

        
                                   
        

