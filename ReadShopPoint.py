import urllib2
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
from ReadAreaList import *
def proc_MapPage(shopId):
    url = 'http://www.dianping.com/shop/%d/map' % shopId

    sleepWait=0
    while 1:
        try:
            domtree = getUrlDomTree(url)
            break
        except Exception, e:
            if isinstance(e,urllib2.HTTPError):
                if e.code/100==4:
                    conn_task.execute('update shopIds set proced=1,time=CURRENT_TIMESTAMP where id=?',(shopId,))
                    conn_task.commit()
                    return
                if e.code/100==5:
                    sleepWait+=3*60
                    if sleepWait>9*60:
                        sleepWait=9*60
            else:
                sleepWait=10
            print url
            print e
            time.sleep(sleepWait)
            continue

    html_root = FindSubNode(domtree, 'html')
    html_body = FindSubNode(html_root, 'body')
    for one in html_body.childNodes:
        if one.type == 5:
            if one.name == 'script':
                for second in one.childNodes:
                    if second.type == 4:
                        re_res = re.search('^\s*var\s+page\s*=', second.value, re.IGNORECASE)
                        if re_res != None:
                            start = second.value.find('{')
                            end = second.value.find('}')
                            #jobject=json.load(StringIO(second.value[start:end+1]))
                            all_word = second.value[start + 1:end].split(',')
                            all_list = {}
                            for pair in all_word:
                                kvl = pair.split(':')
                                if len(kvl) < 2:
                                    continue
                                all_list[kvl[0].strip()] = kvl[1].strip(' \r\n"')
                            if len(all_list['p'])==0:
                                conn_task.execute('update shopIds set proced=1,time=CURRENT_TIMESTAMP where id=?',(shopId,))
                                conn_task.commit()
                                return
                            msg_list_tmp = re.split('<.*?>', all_list['msg'])
                            msg_list = []
                            for spltmsg in msg_list_tmp:
                                spltmsg2 = spltmsg.strip()
                                if len(spltmsg2) > 0:
                                    msg_list.append(spltmsg2)
                            oneShop = {
                                    'poi':all_list['p'],
                                     'pos':decodeDP_POI(all_list['p']),
                                     'shopId':string.atoi(all_list['shopId'])
                                     }
                            if len(msg_list) > 0:
                                oneShop['shopName'] = msg_list[0]
                            if len(msg_list) > 1:
                                oneShop['address'] = msg_list[1]

                            conn.execute('replace into shop_list(shopId,lat,lng,address,shopname,poi) values(?,?,?,?,?,?)',
                                         (oneShop['shopId'],oneShop['pos']['lat'],oneShop['pos']['lng'],oneShop.get('address'),oneShop.get('shopName'),oneShop['poi']))
                            conn_task.execute('update shopIds set proced=1,time=CURRENT_TIMESTAMP where id=?',(oneShop['shopId'],))
                            conn.commit()
                            conn_task.commit()
                            print '%d has done'%oneShop['shopId']

if __name__ == '__main__':
    conn = sqlite3.connect(cur_file_dir()+'/../fetchDianPin/dianpinData.db')
    try:
        conn.execute('create table shop_list(shopId int not null,lat float not null ,lng float not null,address varchar(255),shopname varchar(255),time TIMESTAMP default CURRENT_TIMESTAMP,poi varchar(16),primary key(shopId))')
    except Exception,e:
        print e
    conn.commit()

    try:
		conn_task=conn
		task_cursor=conn_task.cursor()
		while 1:
			task_cursor.execute('select id from shopIds where proced==0 limit 20')
			task_list=task_cursor.fetchall()
			if len(task_list)==0:
				break

			for task in task_list:
				proc_MapPage(task[0])
    except Exception,e:
        print e
    print '\a\a'