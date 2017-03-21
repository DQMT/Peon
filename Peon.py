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
        self.filename = 'cookie.txt'
        self.threadException = ['thread-12796133-1-1.html','thread-10822419-1-1.html','thread-13044278-1-1.html','thread-12975130-1-1.html','thread-13281309-1-1.html','thread-12992527-1-1.html']

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
        print 'threadsList count',count
        return threadsList

    def getPageCount(self,contents):
        #print contents
        soup = BeautifulSoup(contents, "html.parser")
        #reps = soup.findAll(name='a',attrs={"href":re.compile(r'^thread-.*html$')})
        #reps = soup.findAll(name='span',attrs={"title":re.compile(r'.* \d .*')})
        reps = soup.findAll(name='span',attrs={"title":re.compile(r'.* \d .*')})

        #print reps[0].attrs['title']
        try:
            items = re.findall(r"\d",reps[0].attrs['title'])
        except Exception,e:
            if hasattr(e,"code"):
                print e.code
            if hasattr(e,"reason"):
                print e.reason
            items = ['']   
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
        print 'getting my reply for ',thread
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

        if maxc < 3:
            return ''
        return maxitem
            
            
            
        
        
        

    def doThread(self,thread):
        if thread in self.threadException:
            print 'pass over thread',thread
            return
        text = self.getMyReply(thread)
        pass
        
        

    def doPage(self,pageIndex):
        contents = self.getPageContents(pageIndex)
        threads = self.getThreads(contents)
        for thread in threads:
            self.doThread(thread)

    def make_cookie(self,name,value):
        return cookielib.Cookie(
            version=0,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain=self.sgURL,
            domain_specified=True,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest=None
        )

    def set_cookie(self,cookie,valString):
        vals = valString.split(':',1)
        valsArray = vals[1].split(';')
        print valsArray
        for val in valsArray:
            entry = val.split('=',1)
            cookie.set_cookie(self.make_cookie(entry[0][1:], entry[1]))
        return cookie

 
    def tryReply(self,thread,text):
        requrl = self.sgURL +'forum.php?mod='
        requrl1 = requrl + 'post&action=reply&fid=44&tid='+thread[7:-9]+'&extra=page%3D1&page=1&infloat=yes&handlekey=reply&inajax=1&ajaxtarget=fwin_content_reply HTTP/1.1'
        requrl2 = requrl + 'ajax&action=checkpostrule&inajax=yes&ac=reply HTTP/1.1'
        requrl3 = requrl + 'post&infloat=yes&action=reply&fid=44&extra=page%3D1&tid='+thread[7:-9]+'&replysubmit=yes&inajax=1 HTTP/1.1'
        formhash = 'fbf62193&handlekey=reply&noticeauthor=&noticetrimstr=&noticeauthormsg=&usesig=0&subject=&message=r%E7%A5%9E%EF%BC%9A%E4%B8%8D%E8%A6%81%E6%80%95%EF%BC%8C%E6%88%91%E6%98%AF%E8%87%AA%E5%B7%B1%E4%BA%BA'
        message = urllib.quote(text)
        print 'url = ',requrl3

        #声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
        #cj = cookielib.MozillaCookieJar(self.filename)
        
        
        cj = cookielib.CookieJar()
        valString = 'Cookie: BAIDU_SSP_lcr=https://www.baidu.com/link?url=38NCK7Trg1iOv4Tjbzu8EdmXBEqQk1rbt9YLe53MwqiM7oRv5El1qxmFaOk-DvFW&wd=&eqid=a20d6be4000b0d910000000458cb5b81; iaFarmuser=iafram; tjpctrl=1490086194521; U6IV_2132_saltkey=OqWgO2kq; U6IV_2132_lastvisit=1490080799; U6IV_2132_atarget=1; U6IV_2132_visitedfid=44; U6IV_2132_seccode=382265.2d4e21b4e1ad9907c9; U6IV_2132_ulastactivity=1490084440%7C0; U6IV_2132_lastcheckfeed=9009365%7C1490084440; U6IV_2132_lip=218.75.68.70%2C1490084440; U6IV_2132_security_cookiereport=c18f0ZNFn%2F5Ad5JvD0HB2mCUkbam3gxZe6ey%2FzjMuggn5ZnGB81E; U6IV_2132_auth=e831UiI5%2BT8mb8ZBKh6gn08UKs5b7FWS6U4cJiyZU2cUS8Zdb2MoyYZXh7A8TLNdPGvjvlx8AccsXP5w0MWWuh0LhfbB; U6IV_2132_st_t=9009365%7C1490084444%7Ca71ffe9d7e7ed553cbdb896e60dede4f; U6IV_2132_forum_lastvisit=D_44_1490084444; U6IV_2132_st_p=9009365%7C1490084683%7C0087669dbc7fe5fd21f6f839b6a14718; U6IV_2132_viewid=tid_13299222; sg_cblzb=0; U6IV_2132_smile=1D1; pgv_pvi=8554387980; pgv_info=ssi=s4863812589; Hm_lvt_bcf12fa2ce69a5732226b5052e39a17a=1489048376,1489451192,1489639322,1489722246; Hm_lpvt_bcf12fa2ce69a5732226b5052e39a17a=1490084684; U6IV_2132_lastact=1490084684%09misc.php%09patch; U6IV_2132_connect_is_bind=0'
        

        #cj = cookielib.MozillaCookieJar()
        #cj.load('cookie.txt', ignore_discard=True, ignore_expires=True)

        
        
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        response = opener.open(self.siteURL)
        print response.read()
        #cj = self.set_cookie(cj,valString)
        
        #保存cookie到文件
        #cj.save(ignore_discard=True, ignore_expires=True)

        #opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')] 
        urllib2.install_opener(opener);
        
        request = urllib2.Request(url = requrl2)

        request.add_header('Accept', '*/*')
        request.add_header('Accept-Encoding', 'gzip, deflate, sdch')
        request.add_header('Accept-Language', 'zh-CN,zh;q=0.8')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')
        request.add_header('X-Requested-With', 'XMLHttpRequest')
        request.add_header('Connection', 'keep-alive')
        request.add_header('Host', 'bbs.sgamer.com')
        request.add_header('Cookie', 'BAIDU_SSP_lcr=https://www.baidu.com/link?url=38NCK7Trg1iOv4Tjbzu8EdmXBEqQk1rbt9YLe53MwqiM7oRv5El1qxmFaOk-DvFW&wd=&eqid=a20d6be4000b0d910000000458cb5b81; iaFarmuser=iafram; tjpctrl=1490086194521; U6IV_2132_saltkey=OqWgO2kq; U6IV_2132_lastvisit=1490080799; U6IV_2132_atarget=1; U6IV_2132_visitedfid=44; U6IV_2132_seccode=382265.2d4e21b4e1ad9907c9; U6IV_2132_ulastactivity=1490084440%7C0; U6IV_2132_lastcheckfeed=9009365%7C1490084440; U6IV_2132_lip=218.75.68.70%2C1490084440; U6IV_2132_security_cookiereport=c18f0ZNFn%2F5Ad5JvD0HB2mCUkbam3gxZe6ey%2FzjMuggn5ZnGB81E; U6IV_2132_auth=e831UiI5%2BT8mb8ZBKh6gn08UKs5b7FWS6U4cJiyZU2cUS8Zdb2MoyYZXh7A8TLNdPGvjvlx8AccsXP5w0MWWuh0LhfbB; U6IV_2132_st_t=9009365%7C1490084444%7Ca71ffe9d7e7ed553cbdb896e60dede4f; U6IV_2132_forum_lastvisit=D_44_1490084444; U6IV_2132_st_p=9009365%7C1490084683%7C0087669dbc7fe5fd21f6f839b6a14718; U6IV_2132_viewid=tid_13299222; sg_cblzb=0; U6IV_2132_smile=1D1; pgv_pvi=8554387980; pgv_info=ssi=s4863812589; Hm_lvt_bcf12fa2ce69a5732226b5052e39a17a=1489048376,1489451192,1489639322,1489722246; Hm_lpvt_bcf12fa2ce69a5732226b5052e39a17a=1490084684; U6IV_2132_lastact=1490084751%09forum.php%09ajax; U6IV_2132_connect_is_bind=0')
        
        response = urllib2.urlopen(request,timeout=5)
        print response.read()

        

        request = urllib2.Request(requrl3,urllib.urlencode({"formhash":"fbf62193","handlekey":"reply","noticeauthor":"","noticetrimstr":"","noticeauthormsg":"","usesig":"0","subject":"","message":message}))
        
        request.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        request.add_header('Accept-Encoding', 'gzip, deflate')
        request.add_header('Accept-Language', 'zh-CN,zh;q=0.8')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36')
        request.add_header('Cache-Control', 'max-age=0')
        request.add_header('Connection', 'keep-alive')
        request.add_header('Host', 'bbs.sgamer.com')
        request.add_header('Cookie', 'BAIDU_SSP_lcr=https://www.baidu.com/link?url=38NCK7Trg1iOv4Tjbzu8EdmXBEqQk1rbt9YLe53MwqiM7oRv5El1qxmFaOk-DvFW&wd=&eqid=a20d6be4000b0d910000000458cb5b81; iaFarmuser=iafram; tjpctrl=1490086194521; U6IV_2132_saltkey=OqWgO2kq; U6IV_2132_lastvisit=1490080799; U6IV_2132_atarget=1; U6IV_2132_visitedfid=44; U6IV_2132_seccode=382265.2d4e21b4e1ad9907c9; U6IV_2132_ulastactivity=1490084440%7C0; U6IV_2132_lastcheckfeed=9009365%7C1490084440; U6IV_2132_lip=218.75.68.70%2C1490084440; U6IV_2132_security_cookiereport=c18f0ZNFn%2F5Ad5JvD0HB2mCUkbam3gxZe6ey%2FzjMuggn5ZnGB81E; U6IV_2132_auth=e831UiI5%2BT8mb8ZBKh6gn08UKs5b7FWS6U4cJiyZU2cUS8Zdb2MoyYZXh7A8TLNdPGvjvlx8AccsXP5w0MWWuh0LhfbB; U6IV_2132_st_t=9009365%7C1490084444%7Ca71ffe9d7e7ed553cbdb896e60dede4f; U6IV_2132_forum_lastvisit=D_44_1490084444; U6IV_2132_st_p=9009365%7C1490084683%7C0087669dbc7fe5fd21f6f839b6a14718; U6IV_2132_viewid=tid_13299222; sg_cblzb=0; U6IV_2132_smile=1D1; pgv_pvi=8554387980; pgv_info=ssi=s4863812589; Hm_lvt_bcf12fa2ce69a5732226b5052e39a17a=1489048376,1489451192,1489639322,1489722246; Hm_lpvt_bcf12fa2ce69a5732226b5052e39a17a=1490084684; U6IV_2132_lastact=1490084751%09forum.php%09ajax; U6IV_2132_connect_is_bind=0')

        response = opener.open(request,timeout=5)
        print response.read()
        
        pass
        
            






peon = Peon()

#peon.getMyReply('thread-13286613-1-1.html')
#peon.getMyReply('thread-13290239-1-1.html')
#peon.doPage('1')
peon.tryReply('thread-13300141-1-1.html','真鳖粉都是压对面的好嘛')

                              


        

        
                                   
        

