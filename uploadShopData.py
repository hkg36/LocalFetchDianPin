#! /usr/bin/env python
#coding=utf-8
import sqlite3
from json_connect import *
from ReadAreaList import *
import geooffset

if __name__ == '__main__':
    count=0
    conn = sqlite3.connect(cur_file_dir()+'/../fetchDianPin/AreaShop.db')
    main_c=conn.cursor()
    main_c.execute('select shopId,shopname,tags,lat,lng,address from mastershop where proced=1')
    while 1:
        main_row=main_c.fetchone()
        if main_row==None:
            break
        offsetpos=geooffset.TransRoadToSatellite(main_row[3],main_row[4])
        shopobj={'name':main_row[1],
        'word':main_row[2]+'\n'+main_row[5],
        'lat':offsetpos['lat'],
        'lng':offsetpos['lng']}
        subshoplist=[]
        sub_c=conn.cursor()
        sub_c.execute('select shopId,shopname,tags,lat,lng,address from subshop where master_id=%d'%(main_row[0],))
        while 1:
            sub_row=sub_c.fetchone()
            if sub_row==None:
                break
            offsetpos=geooffset.TransRoadToSatellite(sub_row[3],sub_row[4])
            subshopobj={'name':sub_row[1],
                    'word':sub_row[2]+'\n'+sub_row[5],
                    'lat':offsetpos['lat'],
                    'lng':offsetpos['lng']}
            subshoplist.append(subshopobj)
        shopobj['subshop']=subshoplist
        if len(subshoplist)>0:
            count=count+1
            try:
                req_res=json_request('http://livep.sinaapp.com/dataimport/importgroup.php',{'shop':shopobj})
                if req_res['Result']=='Success':
                    conn.execute("update mastershop set proced=2 where shopid=%d"%(main_row[0],))
                    conn.commit()
                    print "%d uploaded"%(main_row[0],)
            except Exception,e:
                print "something fail %s"%e



