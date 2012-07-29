#! /usr/bin/env python
#coding=utf-8
"""
将店铺归类到大商场，master_id是父级商场的id
"""
import sqlite3
import sys,os
import time
from ReadAreaList import *

if __name__ == '__main__':
    conn = sqlite3.connect(cur_file_dir()+'/../fetchDianPin/AreaShop.db')
    try:
        conn.execute('create table mastershop(shopId int not null,shopname varchar(255),tags varchar(255),lat float not null ,lng float not null,address varchar(255),proced int default 0,primary key(shopId))')
    except Exception,e:
        print e
    try:
        conn.execute('create table subshop(shopId int not null,master_id int not null,shopname varchar(255),tags varchar(255),lat float not null ,lng float not null,address varchar(255),primary key(shopId))')
    except Exception,e:
        print e

    conn.commit()
    conn.execute('attach `%s` as shopdb'%(cur_file_dir()+'/../fetchDianPin/dianpinData.db',))
    conn.execute("insert or ignore into mastershop(shopId,shopname,tags,lat,lng,address) select shopId,shopname,tags,lat,lng,address from shopdb.shopinfo where tags like '%%综合商场%%'")
    conn.commit()

    main_c=conn.cursor()
    main_c.execute('select shopId,shopname,tags,lat,lng from mastershop where proced=0')
    while 1:
        main_row=main_c.fetchone()
        if main_row==None:
            break

        """sub_c=conn.cursor()
        sub_c.execute("select shopId,shopname,tags,lat,lng,address from shopdb.shopinfo where address like '%%%s%%' and lat>%f and lat<%f and lng>%f and lng<%f and shopid!=%d"%
            (main_row[1],main_row[3]-0.005,main_row[3]+0.005,main_row[4]-0.005,main_row[4]+0.005,main_row[0]))
        while 1:
            sub_row=sub_c.fetchone()
            if sub_row==None:
                break
            print sub_row"""

        conn.execute("insert or ignore into subshop(shopId,master_id,shopname,tags,lat,lng,address) select shopId,%d,shopname,tags,lat,lng,address from shopdb.shopinfo where address like '%%%s%%' and lat>%f and lat<%f and lng>%f and lng<%f and shopid!=%d"%
            (main_row[0],main_row[1],main_row[3]-0.005,main_row[3]+0.005,main_row[4]-0.005,main_row[4]+0.005,main_row[0]))
        conn.execute("update mastershop set proced=1 where shopid=%d"%(main_row[0],))
        conn.commit()

        print '%d proced'%(main_row[0],)
