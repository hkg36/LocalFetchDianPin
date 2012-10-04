#coding=utf-8
"""
查找地区商圈，根据点评网的综合商场位置数据，地理聚类出对应数据，以半径5公里为划分范围
"""
#preprocess params
MIN_DIS=0.03 #must in one group
MAX_DIS=0.04  #maybe in one group

import sqlite3
import math
import MinRound
import os
import scipy

db=sqlite3.connect('../fetchDianPin/AreaShop.db')
dc=db.cursor()
all_point=[]
dc.execute('select tags,shopname,lat,lng from mastershop')
for tags,shopname,lat,lng in dc:
    tags=tags.split(',')
    all_point.append({'name':shopname,'point':(lat,lng),'tags':tags})
dc.close()

newcenter=[]
all_point_copy=all_point[:]
while len(all_point_copy)>0:
    nc={'c':all_point_copy[0],'l':[]}
    pt=all_point_copy[0]['point']
    newcenter.append(nc)
    point_rm=[]
    del all_point_copy[0]
    for i in range(0,len(all_point_copy)):
        nowpt=all_point_copy[i]
        nowpt_p=nowpt['point']
        dis=math.sqrt( (pt[0]-nowpt_p[0])**2+(pt[1]-nowpt_p[1])**2 )
        if dis<MIN_DIS:
            nc['l'].append(nowpt)
            point_rm.append(nowpt)
        elif dis <MAX_DIS:
            nc['l'].append(nowpt)
    for rm in point_rm:
        all_point_copy.remove(rm)

centers=[]
for c in newcenter:
    center=c['c']
    list=c['l'][:]
    list.append(center)
    pts=[]
    for one in list:
        pts.append(MinRound.TPoint(one['point'][0],one['point'][1]))

    mr=MinRound.MinRound()
    rc=mr.Run(pts)
    centers.append({'point':rc,'ls':[]})

def DisPoint(a,b):
    return math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2)
while True:
    for point in all_point:
        mindis=1e4
        mindis_center=None
        for center in centers:
            dis=DisPoint(center['point'],point['point'])
            if dis<mindis:
                mindis=dis
                mindis_center=center
        if mindis_center:
            mindis_center['ls'].append(point)

    re_run=False
    for center in centers:
        c_pt_L=[]
        for c_pt in center['ls']:
            c_pt_L.append(MinRound.TPoint(c_pt['point'][0],c_pt['point'][1]))
        if len(c_pt_L)>0:
            mr=MinRound.MinRound()
            rc=mr.Run(c_pt_L)
            center_dis=DisPoint(rc,center['point'])
            center['point']=rc
            if center_dis>0.002:
                re_run=True
    if re_run==False:
        break
    for center in centers:
        center['ls']=[]

for center in centers:
    print center['point'],len(center['ls'])
    all_tags={}
    for c_p in center['ls']:
        for p_tag in c_p['tags']:
            if p_tag in all_tags:
                all_tags[p_tag]+=1
            else:
                all_tags[p_tag]=1

    if u'综合商场' in all_tags:
        del all_tags[u'综合商场']
    max_tag_count=0
    max_tag=None
    for tag in all_tags:
        if all_tags[tag]>max_tag_count:
            max_tag_count=all_tags[tag]
            max_tag=tag
    center['tag']=max_tag

pointdbfile='../fetchDianPin/GeoPointList.db'
if os.path.isfile(pointdbfile):
    os.remove(pointdbfile)
db=sqlite3.connect(pointdbfile)
db.execute('CREATE TABLE GeoWeiboPoint ( id INTEGER PRIMARY KEY,tag varchar(128),lat FLOAT,lng FLOAT,R FLOAT,last_checktime INT DEFAULT 0)')
db.commit()
for center in centers:
    if len(center['ls'])>0:
        db.execute('insert into GeoWeiboPoint(tag,lat,lng,R) values(?,?,?,?)',(center['tag'],center['point'][0],center['point'][1],center['point'][2]))
db.commit()