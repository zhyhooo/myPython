# -*- coding: utf-8 -*-
import urllib, urllib2
import time, random
import bs4
import sys
reload(sys)
sys.setdefaultencoding('utf-8')



def getList(str_url):

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                  AppleWebKit/537.36 (KHTML, like Gecko)'
    values     = {}
    headers    = {'User-Agent': user_agent}
    data       = urllib.urlencode(values)
    
    try:
        request = urllib2.Request(str_url)
        response = urllib2.urlopen(request)
        html = response.read()
        #print html
        qlist = parse_content_page(html)
    except:
        qlist = []
        print 'getQlist error: '+str_url
        
    return qlist

def parse_content_page(html):
    soup = bs4.BeautifulSoup(html)
    try:
        listbox      = soup.find('div', attrs={'class':'mainbox'}).find('div', attrs={'class':'left_bar'})
        lists  = listbox.find('ul', attrs={'class':'b_strategy_list'}).findAll('li', attrs={'class':'list_item'})
    except:
        lists   = []


    qlist = []
    print len(lists)
    for li in lists:
        titurl = li.find('h2', attrs={'class':'tit'}).find('a')['href']
        titurl = "http://travel.qunar.com%s" %(titurl)
        qlist.append(titurl)

    return qlist
        

def getQinfo(str_url):

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) \
                  AppleWebKit/537.36 (KHTML, like Gecko)'
    values     = {}
    headers    = {'User-Agent': user_agent}
    data       = urllib.urlencode(values)
   
    try:
        request = urllib2.Request(str_url)
        response = urllib2.urlopen(request)
        html = response.read()
        qdetail = parse_question(html)
    except:
        qdetail = []
        print 'getQinfo error: '+str_url
        
    return qdetail

def parse_question(html):
    soup = bs4.BeautifulSoup(html)
    tags = '##'
    
    
    div    = soup.find('div', attrs={'class':'q_skin'}).find('div', attrs={'class':'container'})
    ulist  = div.find('div', attrs={'class':'float_left'}).find('div',attrs={'class':'journey_ct'}).find('ul', attrs={'class':'list_item'})
    days = ulist.findAll('li', attrs={'class':'list'})

    results = []
    for day in days:
        nday = day.find('div', attrs={'class':'day_box'}).find('a').text
        city = day.find('dt', attrs={'class':'tit'}).text
        spotlinks = day.find('dd', attrs={'class':'des'}).findAll('a')
        spots = [ x.text for x in spotlinks ]
        results.append( (nday, city, spots) )

    return results



if __name__ == '__main__':

    flist = 'plan_beijing.txt'
    fdetail = 'plan_detail_beijing.txt'

    qlist = []
    with open(flist, 'w') as fout:
        for i in xrange(1, 302):
            request_url = 'http://travel.qunar.com/travelbook/list/22-beijing-299914/start_heat/%s.htm' % str(i)
            spotlist = getList(request_url)
            ## cn_tit, en_tit, rank, desp, titurl, imgurl
            print >>fout, '\n'.join(spotlist)
            qlist.extend(spotlist)
            seconds = random.random()*2 + 1
            time.sleep(seconds)
            print i
            
    print 'getQlist done...'
   
    with open(fdetail, 'w') as fout:
        for request_url in qlist:
            page_detail =  getQinfo(request_url)
            if page_detail == None:
                continue
            print >>fout, request_url
            for item in page_detail:
                print >>fout, item[0],'$$', item[1], '$$', '+'.join(item[2])
            print >>fout
            
            time.sleep(random.random()*2 + 1)
            print request_url
    
