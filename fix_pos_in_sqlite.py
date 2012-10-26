from ReadAreaList import *
import decode_mapbar
import sqlite3

conn = sqlite3.connect(cur_file_dir()+'/../fetchDianPin/dianpinData.db')
cur=conn.cursor()
cur.execute('select shopId,poi from shop_list')
poilist={}
for sid,poi in cur:
    point=decodeDP_POI(poi)
    point2=decode_mapbar.croodOffsetDecrypt(point['lng'],point['lat'])
    poilist[sid]={'lat':point2[1],'lng':point2[0]}
cur.close()

for sid in poilist:
    point=poilist[sid]
    conn.execute('update shop_list set lat=?,lng=? where shopId=?',(point['lat'],point['lng'],sid))
conn.commit()