#! /usr/bin/env python
#coding=utf-8
import sqlite3
import sys,os
import urllib2
import time
from ReadAreaList import *
if __name__ == '__main__':
    conn = sqlite3.connect(cur_file_dir()+'/../fetchDianPin/dianpinData.db')
    cursor=conn.cursor();
    cursor.execute('select shopid,lat,lng from shop_list')
    while True:
        rows=cursor.fetchmany(50)
        if len(rows)==0:
            break
        for row in rows:
            print row
            url='http://192.168.47.128:8081/geo/save?id=%d&lat=%f&lng=%f'%row
            print url
            request = urllib2.Request(url)
            for i in range(5):
                try:
                    response = urllib2.urlopen(request,timeout=20)
                    content = ReadHttpBody(response)
                    print content
                    break
                except Exception,e:
                    print e
                    time.sleep(5)
