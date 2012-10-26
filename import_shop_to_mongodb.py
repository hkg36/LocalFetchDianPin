#coding=utf-8
import pymongo
import sqlite3
import decode_mapbar
import re
if __name__ == '__main__':
    conn = sqlite3.connect('../fetchDianPin/dianpinData.db')
    dbcur=conn.cursor()
    dbcur.execute('select shopId,lat,lng,address,shopname,poi,tags,aver from shop_list left join shopids on id=shopId')

    mongo_conn=pymongo.Connection('mongodb://xcj.server4,xcj.server2/')

    shops=[]
    count=0
    for shopId,lat,lng,address,shopname,poi,tags,aver in dbcur:
        if lng<-180 or lng>180 or lat<-90 or lat>90:
            mongo_conn.dianpin.shop.update({'dianpin_id':shopId},{'$unset':{'loc':1}})
            count+=1
            continue
        tags=list(set(re.split(r'[\s/,]+',tags)))
        oneline={'dianpin_id':shopId,'loc':{'lat':lat,'lng':lng},'address':address,'shopname':shopname,
                 'dianpin_poi':poi,'dianpin_tag':tags,'aver_cost':aver}
        mongo_conn.dianpin.shop.update({'dianpin_id':shopId},{'$set':oneline},upsert=True)
        #shops.append(oneline)
        if len(shops)>500:
            #mongo_conn.dianpin.shop.insert(shops)
            shops=[]
    if len(shops):
        #mongo_conn.dianpin.shop.insert(shops)
        pass
    print count