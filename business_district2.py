#coding=utf-8
"""
查找地区商圈，根据点评网的综合商场位置数据，地理聚类出对应数据，以半径5公里为划分范围
"""
#preprocess params
MIN_DIS=0.09 #must in one group
MAX_DIS=0.11  #maybe in one group

import sqlite3
import math
import MinRound
import os
import decode_mapbar
import pylab
import json

#db=sqlite3.connect('../fetchDianPin/dianpinData.db')
db=sqlite3.connect('../fetchDianPin/AreaShop.db')
dc=db.cursor()
all_point=[]
#dc.execute('select shopId,tags,shopname,lat,lng from shopinfo')
dc.execute('select shopId,tags,shopname,lat,lng from mastershop')
for shopId,tags,shopname,lat,lng in dc:
    tags=tags.split(',')
    newp=decode_mapbar.croodOffsetDecrypt(lng,lat)
    all_point.append({'name':shopname,'point':(newp[1],newp[0]),'tags':tags,'shopid':shopId})
dc.close()

print 'data loaded'
#猜测初始中心，选择某些点作为中心，这些点周围的点属于这些中心
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
print 'init center (%d)'%len(newcenter)

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
    #合并过于接近的中心
    to_remove_center=[]
    for centerindex in xrange(len(centers)):
        c=centers[centerindex]
        for testpindex in xrange(centerindex+1,len(centers)):
            testp=centers[testpindex]
            if DisPoint(c['point'],testp['point'])<(MIN_DIS/2):
                to_remove_center.append(c)
                break
    for c in to_remove_center:
        centers.remove(c)

    #计算当前中心对应的点
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

    #计算中心移动的距离，移动过大的时候需要重新拟合
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
            if center_dis>(MIN_DIS/4):
                print center_dis
                re_run=True
    #删除没有点的中心
    to_remove_center=[]
    for centerindex in xrange(len(centers)):
        c=centers[centerindex]
        if len(c['ls'])==0:
            to_remove_center.append(c)
    for c in to_remove_center:
        centers.remove(c)
    print '-------------------'
    if re_run==False:
        break
    for center in centers:
        center['ls']=[]

for center in centers:
    print center['point'],len(center['ls'])
    ls=center['ls']
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
    if max_tag!=None:
        center['tag']=max_tag
    else:
        center['tag']=ls[0]['name']
    if len(centers)==1:
        center['centershopid']=ls[0]['shopid']
    else:
        mindis=1e5
        mindisshopid=0
        for cs in ls:
            dis=DisPoint(center['point'],cs['point'])
            if dis<mindis:
                mindis=dis
                mindisshopid=cs['shopid']
        center['centershopid']=mindisshopid

for center in centers:
    cir = pylab.Circle((center['point'][1],center['point'][0]), radius=center['point'][2],facecolor=(0,0,0),
        edgecolor=(0.8,0,0), alpha =.5, fc='b')
    pylab.gca().add_patch(cir)
pylab.scatter([pt['point'][1] for pt in all_point],[pt['point'][0] for pt in all_point])
pylab.axis('scaled')
pylab.show()

pointdbfile='../fetchDianPin/GeoPointList.db'
if os.path.isfile(pointdbfile):
    os.remove(pointdbfile)
db=sqlite3.connect(pointdbfile)
db.execute('CREATE TABLE GeoWeiboPoint ( id INTEGER PRIMARY KEY,tag varchar(128),lat FLOAT,lng FLOAT,R FLOAT,centershopid int)')
db.commit()
for center in centers:
    if len(center['ls'])>0:
        db.execute('insert into GeoWeiboPoint(tag,lat,lng,R,centershopid) values(?,?,?,?,?)',
            (center['tag'],center['point'][0],center['point'][1],center['point'][2],center['centershopid']))
db.commit()