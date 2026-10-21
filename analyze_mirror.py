import re, os
import numpy as np
def load(fn):
    f3=[];f90=[]
    for line in open(fn,errors='ignore'):
        m=re.match(r'^(f3|f90)\s*=\s*([-+0-9.eE]+)',line)
        if m: (f3 if m.group(1)=='f3' else f90).append(float(m.group(2)))
    n=min(len(f3),len(f90)); f3=np.array(f3[:n])/1e6; f90=np.array(f90[:n])/1e6
    x=f3/f90; u=x*x; q=1/np.sqrt((2-(1-u)**2)/u)
    return f3,q
print('mref  T(C)   f3 mean  f3 sd%   Q mean  Q sd%   yield(fixed spec)  n')
for T in ('27','-20'):
    for M in ('1','4','16'):
        fn='results_ptm_m%s_tt_1.8_%s.txt'%(M,T)
        if not os.path.exists(fn): print('%4s %5s  missing'%(M,T)); continue
        f3,q=load(fn)
        y=np.mean((abs(f3-1.6)<=0.16)&(q>=0.6)&(q<=0.8))*100
        print('%4s %5s  %7.3f  %6.2f   %6.3f  %5.2f   %8.1f %%          %d'%(M,T,f3.mean(),f3.std()/f3.mean()*100,q.mean(),q.std()/q.mean()*100,y,len(f3)))
