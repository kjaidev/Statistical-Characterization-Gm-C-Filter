import re, subprocess, os, math, sys
import numpy as np
D='/foss/designs/gmc-filter'; LIB='/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice'
os.chdir(D)
NR=int(sys.argv[1]) if len(sys.argv)>1 else 200
base=open('gmc_pt.spice').read()
def netlist(vin,ctrl,tag):
    t=re.sub(r'(?m)^\.lib .*',".lib %s tt_mm"%LIB,base)
    t=re.sub(r'(?m)^V1 VDD 0 .*','V1 VDD 0 1.8',t)
    t=re.sub(r'(?m)^Vinp .*',vin,t)
    t=re.sub(r'(?m)^\.include .*','.include %s/a10_%s.cir'%(D,tag),t)
    t=re.sub(r'(?m)^\.param .*','.param iref=12u rt=1.48 alpha=0.6',t)
    open('a10_%s.cir'%tag,'w').write(ctrl)
    L=t.split('\n'); L.insert(1,'.temp 27'); open('a10_%s.spice'%tag,'w').write('\n'.join(L))
    return subprocess.run(['ngspice','-b','a10_%s.spice'%tag],capture_output=True,text=True).stdout
def show(name,x,fmt='%.3f'):
    p=np.percentile(x,[5,50,95])
    print(('  %-14s mean '+fmt+'  sd '+fmt+'  min '+fmt+'  p5 '+fmt+'  median '+fmt+'  p95 '+fmt+'  max '+fmt)%(name,x.mean(),x.std(),x.min(),p[0],p[1],p[2],x.max()))
fn='a10_step.txt'
if os.path.exists(fn): os.remove(fn)
ctrl='.control\nsetseed 12345\nset appendwrite\nrepeat %d\n reset\n tran 2n 6u 0 2n\n linearize v(vo2)\n wrdata %s v(vo2)\nend\nquit\n.endc\n'%(NR,fn)
netlist('Vinp vin 0 dc 0.9 ac 1 pwl(0 0.9 10n 1.0)',ctrl,'step')
d=np.loadtxt(fn); n=3001; nrun=len(d)//n
print('step MC: %d rows -> %d runs'%(len(d),nrun))
W=d[:nrun*n,1].reshape(nrun,n); t=d[:n,0]
def cross(w,lvl):
    i=int(np.argmax(w>=lvl))
    return t[i-1]+(lvl-w[i-1])/(w[i]-w[i-1])*(t[i]-t[i-1])
OS=[];TR=[];G=[];OFF=[]
for w in W:
    w0=w[0]; fin=w[-500:].mean(); step=fin-w0
    OS.append(100*(w.max()-fin)/step); G.append(step/0.1); OFF.append((w0-0.9)*1e3)
    TR.append((cross(w,w0+0.9*step)-cross(w,w0+0.1*step))*1e9)
OS=np.array(OS);TR=np.array(TR);G=np.array(G);OFF=np.array(OFF)
show('overshoot %',OS,'%.2f'); show('rise 10-90 ns',TR,'%.1f'); show('DC gain',G,'%.4f'); show('out offset mV',OFF,'%.1f')
print('  (ideal 2nd-order Butterworth, Q=0.707: overshoot 4.3 %)')
