import urllib2,cookielib
import string
import re
from StringIO import StringIO
import gzip
import zlib
import json
import datetime
import html5lib
import sqlite3
import sys,os
import time

cookie=cookielib.CookieJar()
opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
urllib2.install_opener(opener)

def FindSubNode(root, name):
    for one in root.childNodes:
        if one.type == 5:
            if one.name == name:
                 return one
    return None
def SearchSubNodes(root, name, returnlist):
    for one in root.childNodes:
        if one.type == 5:
            if one.name == name:
                 returnlist.append(one)
        SearchSubNodes(one, name, returnlist)

settings = {
            'digi': 16,
            'add': 10,
            'plus': 7,
            'cha': 36,
            'center': {
                'lat': 34.957995,
                'lng': 107.050781,
                'isDef': True
            }
        }
def intToStr(Num, radix):
    if Num<0:
        raise Exception('decode fail')
    _base = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    _res = ''
    while 1:
        _d = Num % radix
        _res += _base[_d]
        Num = Num / radix
        if Num == 0:
            return _res
def decodeDP_POI(a):
    b = -1
    c = 0
    d = ""
    e = len(a)
    g = ord(a[e - 1])
    a = a[0:e-1]
    e-=1
    for f in xrange(e):
        h = string.atoi(a[f], settings['cha']) - settings['add']
        if h >= settings['add']:
            h -= settings['plus']
        d += intToStr(h,settings['cha'])
        if h > c:
            b = f
            c = h

    a = string.atoi(d[0:b],settings['digi'])
    b = string.atoi(d[b + 1:], settings['digi'])
    g = (a + b - g) / 2
    b = float(b - g) / 1E5
    return {
        'lat': b,
        'lng': float(g) / 1E5
    }

def getUrlDomTree(url,ref=None):
    request = urllib2.Request(url)
    request.add_header('Accept-encoding', 'gzip')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.162 Safari/535.19')
    if ref!=None:
        request.add_header('Referer',ref)
    response = urllib2.urlopen(request,timeout=20)
    content = ReadHttpBody(response)

    ct_str = response.info().get('Content-Type')
    if ct_str != None:
        re_res = re.search(';\s*charset\s*=\s*([\w\d-]+)', ct_str, re.IGNORECASE)
        if re_res != None:
            encode = re_res.group(1)
        else:
            encode = None

    parser = html5lib.HTMLParser()
    return parser.parse(content, encoding=encode)

def ReadHttpBody(response):
    cl = response.info().getheader('Content-length');
    if cl == None:
        cl = 0;
    else:
        cl = string.atoi(cl);
    if cl == 0:
        content = response.read();
    else:
        content = response.read(cl);
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(content)
        f = gzip.GzipFile(fileobj=buf)
        content = f.read()
    elif response.info().get('Content-Encoding') == 'deflate':
        content = zlib.decompress(content)
    return content
def ReadAllList(id):
    url = 'http://www.dianping.com/shopall/%d/0' % id
    try:
       domtree = getUrlDomTree(url)
    except Exception, e:
       print e
       return

    try:
        for node in iter(domtree):
           if node.type == 5 and node.name == 'a':
               if node.attributes.get('name') == 'BDBlock':
                   frelist = node.parent.parent
                   prenode = node.parent
                   break
        for i in range(len(frelist.childNodes)):
            if frelist.childNodes[i] == prenode:
                checknode = frelist.childNodes[i + 1]
                break
    except Exception, e:
       print e
       return
    link_list = []
    for node in checknode.childNodes:
        if node.type == 5 and node.name == "dl":
            SearchSubNodes(node, 'a', link_list)
    for linkNode in link_list:
        hrefstr = linkNode.attributes.get('href')
        if hrefstr != None:
            re_res = re.search('/search/category/(\d+)/0/r(\d+)', hrefstr, re.IGNORECASE)
            if re_res != None:
                a = string.atoi(re_res.group(1))
                r = string.atoi(re_res.group(2))
                conn.execute('insert or ignore into category_list(a,r) values(?,?)',(a,r))
    conn.commit()

def proc_Category(a,r):
    max_page=51
    for p in range(1,51):
        if p>max_page:
            break
        url = 'http://www.dianping.com/search/category/%d/0/r%dp%d' % \
            (a,r,p)

        sleepWait=0
        while True:
            try:
                domtree = getUrlDomTree(url)
                break
            except Exception, e:
                sleepWait+=60
                print url
                print e
                time.sleep(sleepWait)

        searchList = None
        for node in iter(domtree):
            if node.type == 5 and node.name == 'div' :
                idstr = node.attributes.get('id')
                if   idstr != None and idstr.lower() == 'searchlist':
                    searchList = node
                    break
        if p==1:
            for node in iter(domtree):
                if node.type==5 and node.name=='div' and node.attributes.get('class')=='Pages':
                    find_max_page=0
                    for subnode in node.childNodes:
                        if subnode.type==5 and subnode.name=='a':
                            hrefstr=subnode.attributes.get('href')
                            if hrefstr!=None:
                                re_res = re.search('/search/category/\d+/\d+/r\d+p(\d+)', hrefstr, re.IGNORECASE)
                                if re_res!=None:
                                    pnum=string.atoi(re_res.group(1))
                                    if find_max_page<pnum:
                                        find_max_page=pnum
                    max_page=find_max_page
                    print 'max page=%d'%max_page
                    break

        if searchList == None:
            return
        searchdl = FindSubNode(searchList, 'dl')
        shopid_list = []
        for node in searchdl.childNodes:
            if node.type == 5 and node.name == 'dd':
                pnode = None
                tagsNode=None
                for subnode in node.childNodes:
                    if subnode.type == 5 and subnode.name == 'p':
                        pnode = subnode
                    elif subnode.type == 5 and subnode.name == 'ul' and subnode.attributes.get('class')=='detail':
                        for ftag in subnode.childNodes:
                            if ftag.type==5 and ftag.name=='li' and ftag.attributes.get('class')=='tags':
                                tagsNode=ftag
                                break

                tag_list=[]
                if tagsNode!=None:
                    for subnode in tagsNode.childNodes:
                        if subnode.type==5 and subnode.name=='a':
                            tagName=''
                            for textNode in subnode.childNodes:
                                if textNode.type==4:
                                    tagName+=textNode.value
                            tag_list.append(tagName)

                if pnode != None:
                    for anode in iter(pnode):

                        if anode.type == 5 and anode.name == 'a':
                            hrefmap = anode.attributes.get('href')
                            if hrefmap != None:
                                re_res = re.search('/shop/(\d+?)/map', hrefmap, re.IGNORECASE)
                                if re_res != None:
                                    find_shopNum = re_res.group(1)
                                    shopid_list.append((string.atoi(find_shopNum),','.join(tag_list)))
                                    break


        for info in shopid_list:
            conn.execute('insert or ignore into shopIds(id,tags) values(?,?)',info)
    conn.execute('update category_list set proced=1,time=CURRENT_TIMESTAMP where a=? and r=?',(a,r))
    conn.commit()

def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)

if __name__ == '__main__':
    conn = sqlite3.connect(cur_file_dir()+'/../fetchDianPin/dianpinData.db')
    try:
        conn.execute('create table category_list(a int not null,r int not null,proced int default 0,time TIMESTAMP default CURRENT_TIMESTAMP,primary key(a,r))')
    except Exception,e:
        print e
    try:
        conn.execute('create table shopIds(id int not null,tags varchar(255),proced int default 0,time TIMESTAMP default CURRENT_TIMESTAMP,primary key(id))')
    except Exception,e:
        print e
    conn.commit()
    if len(sys.argv)>=2:
        id=string.atoi(sys.argv[1])
        ReadAllList(id)
    cc=conn.cursor()
    cc.execute('select a,r from category_list where proced=0')
    all_list=cc.fetchall()
    for row in all_list:
        try:
            proc_Category(row[0],row[1])
            print 'proc %d %d done'%row
        except Exception,e:
            print e
            conn.rollback()
    conn.close()