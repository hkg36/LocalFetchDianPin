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

def TransRoadToSatellite(lat,lng):
    geoconn=sqlite3.connect(cur_file_dir()+'/../fetchDianPin/geooffset.db')
    des_lat6=lat*1e6
    des_lng6=lng*1e6
    geo_cursor=geoconn.cursor()
    geo_cursor.execute('SELECT id,(?-des_lat+src_lat),(?-des_lng+src_lng) FROM geo_offset order by abs(?-des_lat)+abs(?-des_lng) limit 1',(des_lat6,des_lng6,des_lat6,des_lng6))
    geo_list=geo_cursor.fetchall()
    return {'id':geo_list[0][0],
        'lat':geo_list[0][1]/1e6,
        'lng':geo_list[0][2]/1e6
        }
def TransSatelliteToRoad(lat,lng):
    geoconn=sqlite3.connect(cur_file_dir()+'/../fetchDianPin/geooffset.db')
    des_lat6=lat*1e6
    des_lng6=lng*1e6
    geo_cursor=geoconn.cursor()
    geo_cursor.execute('SELECT id,(?-src_lat+des_lat),(?-src_lng+des_lng) FROM geo_offset order by abs(?-src_lat)+abs(?-src_lng) limit 1',(des_lat6,des_lng6,des_lat6,des_lng6))
    geo_list=geo_cursor.fetchall()
    return {'id':geo_list[0][0],
        'lat':geo_list[0][1]/1e6,
        'lng':geo_list[0][2]/1e6
        }

if __name__ == '__main__':
    lat=29.566305
    lng=106.553765
    res=TransSatelliteToRoad(lat,lng)
    print res
