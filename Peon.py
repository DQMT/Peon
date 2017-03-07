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
        self.sgURL = "http://bbs.sgamer.com/"
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
        reps = soup.findAll(name='a',attrs={"href":re.compile(r'^thread-.*html$'),"onclick":"atarget(this)"})
        count = 0
        for rep in reps:
            count = count + 1
            threadsList.append(rep.attrs['href'])
        print 'count',count
        return threadsList

    def getPageCount(self,contents):
        #print contents
        soup = BeautifulSoup(contents, "html.parser")
        #reps = soup.findAll(name='a',attrs={"href":re.compile(r'^thread-.*html$')})
        #reps = soup.findAll(name='span',attrs={"title":re.compile(r'.* \d .*')})
        reps = soup.findAll(name='span',attrs={"title":re.compile(r'.* \d .*')})

        #print reps[0].attrs['title']
        items = re.findall(r"\d",reps[0].attrs['title'])
        print 'total pages = ',items[0]
        return items[0]
        

    def getReplies(self,thread):
        replyList = list()
        url = self.sgURL + thread
        contents = self.getUrlContents(url)
        #print contents
        pageCount = self.getPageCount(contents)
        if not pageCount.isdigit():
            pageCount = 1
        if pageCount > 9:
            pageCount = 9
        for i in range(1,pageCount + 1):
            url = url[:-8]+('%d' %i)+url[-7:]
            #print 'url',url
            contents = self.getUrlContents(url)
            soup = BeautifulSoup(contents, "html.parser")
            reps = soup.findAll(name='td',attrs={"id":re.compile(r'^postmessage_\d*$'),"class":"t_f"})
            for rep in reps:
                div_quote = rep.div
                if div_quote is None:
                    pass
                else:
                    div_quote.decompose()
                
                replyList.append(rep.text.strip())
        return replyList
    

    def getMyReply(self,thread):
        replyList = self.getReplies(thread)
        myReply = self.getMostReply(replyList)
        print 'myReply =',myReply
        return myReply


    def getMostReply(self,replyList):
        if not replyList:
            return ''
        myset = set(replyList)
        maxc = 0
        maxitem = replyList[0]
        #print 'maxitem',maxitem
        for item in myset:
            if replyList.count(item) > maxc:
                maxc = replyList.count(item)
                maxitem = item
            #print("the %s has found %d" %(item,replyList.count(item)))
        #print 'most reply',maxitem
        return maxitem
            
            
            
        
        
        

    def doThread(self,thread):
        
        pass
        
        

    def doPage(self,pageIndex):
        contents = self.getPageContents(pageIndex)
        threads = self.getThreads(contents)
        for thread in threads:
            self.doThread(thread)
            






peon = Peon()

#peon.getMyReply('thread-13286613-1-1.html')
peon.getMyReply('thread-13288501-1-1.html')


                              


        

        
                                   
        

