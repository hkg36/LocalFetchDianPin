#coding=utf-8
import sqlite3
from MinRound import *
import os


db=sqlite3.connect('../fetchDianPin/AreaShop.db')
dc=db.cursor()
dc.execute('select tags from mastershop group by tags')
all_tag=[]
for tags, in dc:
    all_tag.append({'tag':tags,'points':[]})
for line in all_tag:
    dc.execute('select shopname,lat,lng from mastershop where tags=?',(line['tag'],))
    points=line['points']
    for shopname,lat,lng in dc:
        points.append({'name':shopname,'point':(lat,lng)})
dc.close()
print len(all_tag)
def RunLineRound(line):
    points=line['points']
    pl=[]
    for p in points:
        ll=p['point']
        pl.append(TPoint(ll[0],ll[1]))
    mr=MinRound()
    return mr.Run(pl)
for line in all_tag:
    pr=RunLineRound(line)
    line['round']=pr

new_all_tag=[]
for line in all_tag:
    if line['round'][2]>0.05:
        points=line['points'][:]

        newcenter=[]
        while len(points)>0:
            nc={'c':points[0],'l':[]}
            pt=points[0]['point']
            newcenter.append(nc)
            point_rm=[]
            del points[0]
            for i in range(0,len(points)):
                nowpt=points[i]
                nowpt_p=nowpt['point']
                dis=math.sqrt( (pt[0]-nowpt_p[0])**2+(pt[1]-nowpt_p[1])**2 )
                if dis<0.045:
                    nc['l'].append(nowpt)
                    point_rm.append(nowpt)
                elif dis <0.05:
                    nc['l'].append(nowpt)
            for rm in point_rm:
                points.remove(rm)
        for c in newcenter:
            center=c['c']
            list=c['l'][:]
            list.append(center)
            new_line={'tag':line['tag'],'points':list}
            new_all_tag.append(new_line)
    else:
        new_all_tag.append(line)

print len(new_all_tag)
for line in new_all_tag:
    pr=RunLineRound(line)
    line['round']=pr
    if pr[2]>0.04:
        print pr

pointdbfile='../fetchDianPin/GeoPointList.db'
if os.path.isfile(pointdbfile):
    os.remove(pointdbfile)
db=sqlite3.connect(pointdbfile)
db.execute('CREATE TABLE GeoWeiboPoint ( id INTEGER PRIMARY KEY,tag varchar(128),lat FLOAT,lng FLOAT,last_checktime INT DEFAULT 0)')
db.commit()
for line in new_all_tag:
    db.execute('insert into GeoWeiboPoint(tag,lat,lng) values(?,?,?)',(line['tag'],line['round'][0],line['round'][1]))
db.commit()