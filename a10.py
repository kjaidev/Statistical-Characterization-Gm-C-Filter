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
def sine_set(A,f,tag):
    tstep=1.0/(f*128); tstop=10.0/f
    fn='a10_%s.txt'%tag
    if os.path.exists(fn): os.remove(fn)
    ctrl='.control\nsetseed 12345\nset appendwrite\nrepeat %d\n reset\n tran %g %g 0 %g\n linearize v(vo2)\n wrdata %s v(vo2)\nend\nquit\n.endc\n'%(NR,tstep,tstop,tstep,fn)
    netlist('Vinp vin 0 dc 0.9 ac 1 sin(0.9 %g %g)'%(A,f),ctrl,tag)
    d=np.loadtxt(fn); n=int(round(tstop/tstep))+1
    nrun=len(d)//n
    print('%s: %d rows, %d pts/run -> %d runs'%(tag,len(d),n,nrun))
    d=d[:nrun*n,1].reshape(nrun,n)
    G=[];TH=[];H2=[];H3=[]
    for w in d:
        s=w[n-641:n-1]; V=np.fft.rfft(s-s.mean())/len(s)*2
        h=[abs(V[5*k]) for k in range(1,6)]
        G.append(20*math.log10(h[0]/A)); TH.append(100*math.sqrt(sum(x*x for x in h[1:]))/h[0])
        H2.append(20*math.log10(max(h[1],1e-12)/h[0])); H3.append(20*math.log10(max(h[2],1e-12)/h[0]))
    return np.array(G),np.array(TH),np.array(H2),np.array(H3)
def show(name,x,fmt='%.3f'):
    p=np.percentile(x,[5,50,95])
    print(('  %-12s mean '+fmt+'  sd '+fmt+'  min '+fmt+'  p5 '+fmt+'  median '+fmt+'  p95 '+fmt+'  max '+fmt)%(name,x.mean(),x.std(),x.min(),p[0],p[1],p[2],x.max()))
for A,f,tag in ((0.1,200e3,'s200k'),(0.05,1.6e6,'s1p6M')):
    G,TH,H2,H3=sine_set(A,f,tag)
    print('\nsine MC: %.0f mV pk at %.1f kHz (n=%d)'%(A*1e3,f/1e3,len(G)))
    show('gain dB',G); show('THD %',TH); show('HD2 dB',H2,'%.1f'); show('HD3 dB',H3,'%.1f')
    print('  fraction with THD<1%%: %.1f %%   THD<0.5%%: %.1f %%'%(100*np.mean(TH<1),100*np.mean(TH<0.5)))
fn='a10_step.txt'
if os.path.exists(fn): os.remove(fn)
ctrl='.control\nsetseed 12345\nset appendwrite\nrepeat %d\n reset\n tran 2n 6u 0 2n\n linearize v(vo2)\n wrdata %s v(vo2)\nend\nquit\n.endc\n'%(NR,fn)
netlist('Vinp vin 0 dc 0.9 ac 1 pwl(0 0.9 10n 1.0)',ctrl,'step')
d=np.loadtxt(fn); n=3001; nrun=len(d)//n
print('\nstep MC: %d rows -> %d runs'%(len(d),nrun))
W=d[:nrun*n,1].reshape(nrun,n); t=d[:n,0]
def cross(w,lvl):
    i=int(np.argmax(w>=lvl))
    return t[i-1]+(lvl-w[i-1])/(w[i]-w[i-1])*(t[i]-t[i-1])
OS=[];TR=[];FIN=[]
for w in W:
    fin=w[-500:].mean(); step=fin-0.9
    OS.append(100*(w.max()-fin)/step); FIN.append(fin)
    TR.append((cross(w,0.9+0.9*step)-cross(w,0.9+0.1*step))*1e9)
OS=np.array(OS);TR=np.array(TR);FIN=np.array(FIN)
show('overshoot %',OS,'%.2f'); show('rise 10-90 ns',TR,'%.1f'); show('DC gain (step)',(FIN-0.9)/0.1,'%.3f')
print('  (ideal 2nd-order Butterworth, Q=0.707: overshoot 4.3 %)')
