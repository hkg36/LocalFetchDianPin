#! /usr/bin/env python
#coding=utf-8
import sqlite3
import time
from json_connect import *
from ReadAreaList import *
import geooffset

if __name__ == '__main__':
    urllist=['http://www.qqpk.cn/Article/Special/nvtou/List_1.htm',
    'http://www.qqpk.cn/Article/Special/nvtou/',
    'http://www.qqpk.cn/Article/Special/nvtou/List_4.htm',
    'http://www.qqpk.cn/Article/Special/nvtou/List_3.htm',
    'http://www.qqpk.cn/Article/Special/nvtou/List_2.htm']
    count=0
    conn = sqlite3.connect(cur_file_dir()+'/../fetchDianPin/MMHeads.db')
    try:
        conn.execute('create table headurl(url varchar(1024) primary key)')
    except Exception,e:
        print e
    main_c=conn.cursor()


    urlnext=[]
    for url in urllist:
        print 'read main url %s'%url
        while 1:
            try:
                domtree=getUrlDomTree(url,ref='http://www.qqpk.cn/Article/biaoqing/')
                break
            except Exception,e:
                print e;
                time.sleep(5)

        searchList=None
        for node in iter(domtree):
            if node.type == 5 and node.name == 'div' :
                idstr = node.attributes.get('class')
                if   idstr != None and idstr.lower() == 'index_list13':
                    searchList = node
                    break
        reslist=[]
        if searchList!=None:
            SearchSubNodes(searchList,'a',reslist)
            for alink in reslist:
                urlnext.append('http://www.qqpk.cn'+alink.attributes.get('href'))

    for url in  urlnext:
        print 'read sub url %s'%url
        while 1:
            try:
                domtree=getUrlDomTree(url,ref='http://www.qqpk.cn/Article/biaoqing/')
                break
            except Exception,e:
                print e;
                time.sleep(5)

        searchList=None
        for node in iter(domtree):
            if node.type == 5 and node.name == 'div' :
                idstr = node.attributes.get('id')
                if   idstr != None and idstr.lower() == 'content_text':
                    searchList = node
                    break
        print 'sub found'
        reslist=[]
        if searchList!=None:
            SearchSubNodes(searchList,'img',reslist)
            for imglink in reslist:
                imgurl='http://www.qqpk.cn'+imglink.attributes.get('src')
                conn.execute("insert or ignore into headurl(url) values('%s')"%imgurl)

        conn.commit()