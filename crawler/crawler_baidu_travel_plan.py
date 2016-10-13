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
    except Exception as e:
        qlist = []
        print e
        print 'getQlist error: '+str_url
        
    return qlist

def parse_content_page(html):
    soup = bs4.BeautifulSoup(html)
    try:
        listbox  = soup.find('div', attrs={'class':'plan-index'}).find('div', attrs={'class':'index-main'}).find('div', attrs={'class':'good-container'})
        lists  = listbox.find('div', attrs={'clearfix':''}).findAll('li', attrs={'class':'list-item'})
    except:
        lists   = []


    qlist = []
    #print listbox
    for li in lists:
        div = li.find('div', attrs={'class':'plan-info'})
        titurl = "http://lvyou.baidu.com" + div.find('a')['href']
        title = div.find('a').text.strip()
        dest = div.find('p', attrs={'class':'plan-trip'}).find('a').text
        ndays = div.find('p', attrs={'class':'plan-trip-day'}).text[5:]

        qlist.append((titurl,title, dest, ndays))

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
    except Exception as e:
        qdetail = []
        print e
        print 'getQinfo error: '+str_url
        
    return qdetail

def parse_question(html):
    soup = bs4.BeautifulSoup(html)
    
    div    = soup.find('div', attrs={'class':'view-page-container'}).find('div', attrs={'class':'plan-paths'}).find('div', attrs={'class':'paths-list'})
    pathlist = div.findAll('section', attrs={'class':'day-path-main'})
    #print soup.find('div', attrs={'class':'bgf2f2f2'}).find('div', attrs={'class':'ctd_main_body'})
    
    paths = []
    for sect in pathlist:
        dayIdx = sect.find('div', attrs={'class':'day-index'}).text
        try:
            dest = sect.find('strong').text.strip()
        except:
            continue
        spots = [x.text.encode('utf8') for x in sect.find('span', attrs={'class':'day-path-detail'}).findAll('a') ] 
        try:
            comment = sect.find('p', attrs={'class':'day-comment'}).text
        except:
            comment = "N/A"
        paths.append( (dayIdx, dest, spots, comment) )
        #print ' '.join(spots)
    return paths



if __name__ == '__main__':

    flists = 'ctrip_plan_beijing.txt'
    fpages = 'ctrip_plan_detail_beijing.txt'
    qlist = []
    with open(flists, 'w') as fout:
        for i in xrange(0, 25):
            request_url = 'http://lvyou.baidu.com/plan/counselor?surls[]=beijing&days_cnt_low=&days_cnt_high=&pn=%s&rn=30' % str(i*30)
            itemlist = getList(request_url)

            ## titurl,title, dest, ndays
            for item in itemlist:
                print >>fout, item[0]
                print >>fout, item[2], '##', item[3], '##', item[1]
                print >> fout
            qlist.extend(itemlist)
            seconds = random.random()*2 + 1
            time.sleep(seconds)
            print i, len(itemlist)
            
    print 'getQlist done...'

    with open(fpages, 'w') as fout:
        for item in qlist:
            try:
                page = getQinfo(item[0])
                print >>fout, '#titurl#', item[0]
                print >>fout, '#title#', item[2], '##', item[3], '##', item[1]
                #  [(dayIdx, dest, spots, comment)]
                for day in page:
                    print >>fout, '#'+day[0][1:-1]+'#', '##', day[1], '##', '+'.join(day[2])
                    print >>fout, '#comment#', day[3]
                
                print >>fout
                print item[0]
            except Exception as e:
                print e
                print item[0]

