import math
def croodOffsetDecrypt(x,y):
    x = float(x)*100000%36000000;
    y = float(y)*100000%36000000;

    x1 = math.floor(-(((math.cos(y/100000))*(x/18000))+((math.sin(x/100000))*(y/9000)))+x);
    y1 = math.floor(-(((math.sin(y/100000))*(x/18000))+((math.cos(x/100000))*(y/9000)))+y);

    if x>0:
        xoff=1
    else:
        xoff=-1
    if y>0:
        yoff=1
    else:
        yoff=-1
    x2 = math.floor(-(((math.cos(y1/100000))*(x1/18000))+((math.sin(x1/100000))*(y1/9000)))+x+xoff);
    y2 = math.floor(-(((math.sin(y1/100000))*(x1/18000))+((math.cos(x1/100000))*(y1/9000)))+y+yoff);

    return [x2/100000.0,y2/100000.0]
if __name__ == '__main__':
    print croodOffsetDecrypt(114.122145,22.544935)