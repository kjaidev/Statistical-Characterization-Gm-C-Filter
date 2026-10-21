import numpy as np
d=np.array([[float(x) for x in l.split()] for l in open('xy_ac.cir.FD.prn') if len(l.split())==3 and l.split()[0][0].isdigit()])
f=d[:,0]; m=d[:,1]; ph=d[:,2]
if abs(ph).max()<7: ph=np.degrees(ph)
def cross(x,y,lvl):
    for i in range(len(y)-1):
        if (y[i]-lvl)*(y[i+1]-lvl)<=0 and y[i]!=y[i+1]:
            return x[i]+(lvl-y[i])/(y[i+1]-y[i])*(x[i+1]-x[i])
lf=np.log10(f)
f3=10**cross(lf,m,-3)/1e6; f90=10**cross(lf,ph,-90)/1e6
u=(f3/f90)**2; Q=1/np.sqrt((2-(1-u)**2)/u)
print('Xyce    nominal: f3 %.4f MHz  Q %.4f  gain@100k %.3f dB'%(f3,Q,m[0]))
print('ngspice nominal: f3 1.6102 MHz  Q 0.7218  gain@100k -0.150 dB')
