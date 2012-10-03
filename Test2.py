import urllib;
import random;
import string;
from ZODB import FileStorage, DB
while 1:
    lat1=random.uniform(31,32);
    lat2=lat1+0.005
    lng1=random.uniform(121,122);
    lng2=lng1+0.005
    urlstr="http://192.168.47.128:8081/geo/area?lat1=%f&lat2=%f&lng1=%f&lng2=%f"%(lat1,lat2,lng1,lng2);
    print urlstr;
    doc=urllib.urlopen(urlstr);
    resinfo=doc.info();
    len=string.atoi(resinfo['Content-Length']);
    data=doc.read(len);
    print data;