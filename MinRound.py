__author__ = 'amen'
import math
class TPoint:
    def __init__(self,x,y):
        self.x=float(x)
        self.y=float(y)

class MinRound:
    a=[]
    d=TPoint(0,0)
    r=0
    @staticmethod
    def distance(p1,p2):
        return math.sqrt((p1.x-p2.x)*(p1.x -p2.x)+(p1.y-p2.y)*(p1.y-p2.y))
    @staticmethod
    def multiply(p1,p2,p0):
        return   ((p1.x-p0.x)*(p2.y-p0.y)-(p2.x-p0.x)*(p1.y-p0.y))
    def MiniDiscWith2Point(self,p,q,n):
        self.d.x=(p.x+q.x)/2.0
        self.d.y=(p.y+q.y)/2.0
        self.r=MinRound.distance(p,q)/2
        for k in range(0,n):
            if MinRound.distance(self.d,self.a[k])<=self.r:
                continue
            if MinRound.multiply(p,q,self.a[k])!=0.0:
                c1=(p.x*p.x+p.y*p.y-q.x*q.x-q.y*q.y)/2.0
                c2=(p.x*p.x+p.y*p.y-self.a[k].x*self.a[k].x-self.a[k].y*self.a[k].y)/2.0

                self.d.x=(c1*(p.y-self.a[k].y)-c2*(p.y-q.y))/((p.x-q.x)*(p.y-self.a[k].y)-(p.x-self.a[k].x)*(p.y-q.y))
                self.d.y=(c1*(p.x-self.a[k].x)-c2*(p.x-q.x))/((p.y-q.y)*(p.x-self.a[k].x)-(p.y-self.a[k].y)*(p.x-q.x))
                self.r=MinRound.distance(self.d,self.a[k])
            else:
                t1=MinRound.distance(p,q)
                t2=MinRound.distance(q,self.a[k])
                t3=MinRound.distance(p,self.a[k])
                if t1>=t2 and t1>=t3:
                    self.d.x=(p.x+q.x)/2.0
                    self.d.y=(p.y+q.y)/2.0
                    self.r=MinRound.distance(p,q)/2.0
                elif t2>=t1 and t2>=t3:
                    self.d.x=(self.a[k].x+q.x)/2.0
                    self.d.y=(self.a[k].y+q.y)/2.0
                    self.r=MinRound.distance(self.a[k],q)/2.0
                else:
                    self.d.x=(self.a[k].x+p.x)/2.0
                    self.d.y=(self.a[k].y+p.y)/2.0
                    self.r=MinRound.distance(self.a[k],p)/2.0

    def MiniDiscWithPoint(self,pi,n):
        self.d.x=(pi.x+self.a[0].x)/2.0
        self.d.y=(pi.y+self.a[0].y)/2.0
        self.r=MinRound.distance(pi,self.a[0])/2.0

        for j in range(1,n):
            if MinRound.distance(self.d,self.a[j])<=self.r:
                continue
            else:
                self.MiniDiscWith2Point(pi,self.a[j],j)
    def Run(self,pointarray):
        if len(pointarray)==0:
            raise Exception('no point')
        if len(pointarray)==1:
            return (pointarray[0].x,pointarray[0].y,0)
        self.a=pointarray
        self.r=MinRound.distance(self.a[0],self.a[1])/2.0
        self.d.x=(self.a[0].x+self.a[1].x)/2.0
        self.d.y=(self.a[0].y+self.a[1].y)/2.0
        for i in range(2,len(self.a)):
            if MinRound.distance(self.d,self.a[i])<=self.r:
                continue
            else:
                self.MiniDiscWithPoint(self.a[i],i)
        return (self.d.x,self.d.y,self.r)