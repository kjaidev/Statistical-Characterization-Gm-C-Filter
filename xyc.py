import sys, numpy as np
rows=[[float(x) for x in l.split()] for l in open(sys.argv[1]) if len(l.split())==3 and l.split()[0][0].isdigit()]
d=np.array(rows); f,m,ph=d[:,0],d[:,1],d[:,2]
if abs(ph).max()<7: ph=np.degrees(ph)
def cross(x,y,lvl):
    for i in range(len(y)-1):
        if (y[i]-lvl)*(y[i+1]-lvl)<=0 and y[i]!=y[i+1]: return x[i]+(lvl-y[i])/(y[i+1]-y[i])*(x[i+1]-x[i])
lf=np.log10(f); f3=10**cross(lf,m,-3)/1e6; f90=10**cross(lf,ph,-90)/1e6
u=(f3/f90)**2; print('f3 %.4f MHz  Q %.4f'%(f3,1/np.sqrt((2-(1-u)**2)/u)))
